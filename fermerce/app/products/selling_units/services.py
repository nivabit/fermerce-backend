import uuid
import typing as t
from fastapi import status
from tortoise.expressions import Q
from fermerce.app.business.vendor.models import Vendor
from fermerce.app.products.measuring_unit.models import MeasuringUnit
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from fermerce.core.services.base import filter_and_list
from fermerce.lib.errors import error
from fermerce.app.products.selling_units import schemas, models
from fermerce.app.products.product.models import Product
from fastapi import Response


async def create(
    data_in: schemas.IProductSellingUnitIn, vendor: Vendor
) -> models.ProductSellingUnit:
    get_product = await Product.get_or_none(pk=data_in.product_id, vendor=vendor)
    if not get_product:
        raise error.NotFoundError("Product not found")
    get_measuring_unit = await MeasuringUnit.get_or_none(id=data_in.selling_unit_id)
    check_existing_unit = await models.ProductSellingUnit.get_or_none(
        unit=get_measuring_unit, product=get_product
    )
    if check_existing_unit:
        raise error.DuplicateError("product already exists with this unit")
    if not get_measuring_unit:
        raise error.NotFoundError("measuring unit not found")
    check_existing_unit = await models.ProductSellingUnit.get_or_none(
        unit=get_measuring_unit, product=get_product
    )
    if check_existing_unit:
        raise error.DuplicateError(
            f"Measuring unit {get_measuring_unit.unit} already exists for this product"
        )
    selling_unit = await models.ProductSellingUnit.create(
        product=get_product,
        unit=get_measuring_unit,
        price=data_in.price,
        size=data_in.size,
    )
    if not selling_unit:
        raise error.ServerError("Error creating new product measure unit")
    return IResponseMessage(message="Product measure unit created successfully")


async def filter(
    product_id: uuid.UUID,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    load_related: bool = False,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
) -> t.List[models.ProductSellingUnit]:
    query = models.ProductSellingUnit
    if product_id:
        query = query.filter(product=product_id)
    results = await filter_and_list(
        model=models.ProductSellingUnit,
        query=query,
        page=page,
        load_related=load_related,
        per_page=per_page,
        select=select,
        sort_by=sort_by,
        order_by=order_by,
    )
    return results


async def get_selling_unit(
    selling_unit_id: uuid.UUID, vendor: Vendor
) -> t.List[models.ProductSellingUnit]:
    get_selling_unit = await models.ProductSellingUnit.get_or_none(
        pk=selling_unit_id, product__vendor=vendor
    )
    if not get_selling_unit:
        raise error.NotFoundError("product selling unit not found")
    return get_selling_unit


async def get_product_selling_units(
    product_id: uuid.UUID, vendor: Vendor
) -> t.List[models.ProductSellingUnit]:
    get_selling_unit = await models.ProductSellingUnit.filter(
        product=product_id, product__vendor=vendor
    ).all()
    return get_selling_unit


async def update(
    data_in: schemas.IProductSellingUnitIn, vendor: Vendor
) -> models.ProductSellingUnit:
    selling_unit = await models.ProductSellingUnit.get_or_none(
        product=data_in.product_id,
        unit=data_in.selling_unit_id,
        product__vendor=vendor,
    )
    if not selling_unit:
        raise error.NotFoundError("selling unit not found")
    selling_unit.update_from_dict(
        data_in.dict(exclude={"product_id", "selling_unit_id"})
    )
    try:
        await selling_unit.save()
        return selling_unit
    except:
        raise error.ServerError("error updating product selling unit")


async def delete(
    data_in: schemas.IProductRemoveSellingUnitIn, vendor: Vendor
) -> models.ProductSellingUnit:
    get_product = await Product.get_or_none(id=data_in.product_id, vendor=vendor)
    if not get_product:
        raise error.NotFoundError("product not found")
    selling_unit = await models.ProductSellingUnit.filter(
        product=data_in.product_id, id__in=data_in.selling_unit_ids
    ).delete()
    if not selling_unit:
        raise error.NotFoundError("selling unit(s) does not exists for this product")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
