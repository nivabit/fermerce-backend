import uuid
import typing as t
from fastapi import status, Response
from tortoise.expressions import Q
from fermerce.app.vendor.models import Vendor
from fermerce.app.product.models import Product
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from fermerce.core.services.base import filter_and_list
from fermerce.lib.errors import error
from fermerce.app.product_detail import models, schemas


async def create_details(data_in: schemas.IProductDetailsIn, vendor: Vendor):
    get_product = await Product.get_or_none(
        id=data_in.product_id, vendor=vendor
    )
    if not get_product:
        raise error.NotFoundError("product detail not found")
    to_create = [
        models.ProductDetail(**data.dict(), product=get_product)
        for data in data_in.details
    ]
    created_details = await models.ProductDetail.bulk_create(to_create)
    if created_details:
        return IResponseMessage(
            message="Product details was created successfully"
        )
    raise error.ServerError("error creating product details")


async def get_detail(detail_id: uuid.UUID) -> models.ProductDetail:
    product_detail = await models.ProductDetail.get_or_none(id=detail_id)
    if not product_detail:
        raise error.NotFoundError("product detail not found")
    return product_detail


async def filter(
    product_id: uuid.UUID,
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    load_related: bool = False,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
) -> t.List[models.ProductDetail]:
    query = models.ProductDetail
    if product_id:
        query = query.filter(product=product_id)
    if filter_string:
        query = query.filter(
            Q(title__icontains=filter_string)
            | Q(description__icontains=filter_string)
        )

    results = await filter_and_list(
        model=models.ProductDetail,
        query=query,
        page=page,
        load_related=load_related,
        per_page=per_page,
        select=select,
        sort_by=sort_by,
        order_by=order_by,
    )
    return results


async def update_product_detail(
    data_in: schemas.IProductDetailsUpdateIn, vendor: Vendor
) -> models.ProductDetail:
    get_product = await Product.get_or_none(
        id=data_in.product_id, vendor=vendor
    )
    if not get_product:
        raise error.NotFoundError("product not found")

    get_product_detail = await models.ProductDetail.get_or_none(
        id=data_in.detail_id, product=get_product
    )
    if not get_product_detail:
        raise error.NotFoundError("product detail does not exist")
    get_product_detail.update_from_dict(
        data_in.dict(exclude={"product_id", "detail_id"})
    )
    await get_product_detail.save()
    return get_product_detail


async def delete_product_detail(
    data_in: schemas.IProductDetailsRemoveIn, vendor: Vendor
):
    get_product = await Product.get_or_none(
        id=data_in.product_id, vendor=vendor
    )
    if not get_product:
        raise error.NotFoundError("product not found")

    get_product_detail = await models.ProductDetail.filter(
        id__in=data_in.detail_ids, product=get_product
    ).delete()
    if get_product_detail:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise error.NotFoundError("product or product details is not found")
