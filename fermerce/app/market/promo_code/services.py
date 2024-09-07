import uuid
import typing as t
from fastapi import status
from fermerce.app.vendor.models import Vendor
from fermerce.app.product.models import Product
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage, ITotalCount
from fermerce.core.services.base_old import filter_and_list
from fermerce.lib.exceptions import exceptions
from fermerce.app.promo_code import models, schemas
from fastapi import Response


async def create(
    data_in: schemas.IProductPromoCodeIn, vendor: Vendor
) -> models.ProductPromoCode:
    check_code = await models.ProductPromoCode.get_or_none(
        code=data_in.code, vendor=vendor
    )
    if check_code:
        raise exceptions.DuplicateError("product promo code already exists")
    new_code = await models.ProductPromoCode.create(
        **data_in.dict(), vendor=vendor
    )
    if new_code:
        return new_code
    raise exceptions.ServerError("Internal server error")


async def get(
    promo_code_id: uuid.UUID, vendor: Vendor
) -> models.ProductPromoCode:
    code = await models.ProductPromoCode.get_or_none(
        id=promo_code_id, vendor=vendor
    )
    if not code:
        raise exceptions.NotFoundError("Product promo code not found")
    return code


async def filter(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = None,
    order_by: str = None,
    sort_by: SortOrder = SortOrder.asc,
) -> dict:
    query = models.ProductPromoCode
    if filter_string:
        query = query.filter(code__icontains=filter_string)

    results = await filter_and_list(
        model=models.ProductPromoCode,
        query=query,
        per_page=per_page,
        page=page,
        select=select,
        sort_by=sort_by,
        order_by=order_by,
    )
    return results


async def get_total_count(vendor: Vendor) -> ITotalCount:
    total = await models.ProductPromoCode.filter(vendor=vendor).all().count()
    return ITotalCount(count=total).dict()


async def update(
    promo_code_id: uuid.UUID,
    data_in: schemas.IProductPromoCodeIn,
    vendor: Vendor,
) -> models.ProductPromoCode:
    get_promo_code = await models.ProductPromoCode.get_or_none(
        id=promo_code_id, vendor=vendor
    )
    if not get_promo_code:
        raise exceptions.NotFoundError("promo code does not exist")
    check_code = await models.ProductPromoCode.get_or_none(
        code=data_in.code, vendor=vendor
    )
    if check_code and check_code.id != get_promo_code.id:
        raise exceptions.DuplicateError("promo code already exists")
    elif not check_code or check_code and get_promo_code:
        get_promo_code.update_from_dict(data_in.dict())
        await get_promo_code.save()
        return get_promo_code


async def add_product_to_promo_code(
    data_in: schemas.IProductPromoCodeUpdateIn, vendor: Vendor
) -> IResponseMessage:
    get_promo_code = await models.ProductPromoCode.get_or_none(
        id=data_in.promo_code_id, vendor=vendor
    )
    if not get_promo_code:
        raise exceptions.NotFoundError("promo code does not exist")
    check_products = await Product.filter(
        id__in=data_in.products, vendor=vendor
    ).all()
    if not check_products:
        raise exceptions.NotFoundError("No product is found")
    existing_promo_products = await get_promo_code.products.all()
    for index, product in enumerate(check_products):
        if product in existing_promo_products:
            check_products.pop(index)
    await get_promo_code.products.add(*check_products)
    return IResponseMessage(message="Product/products was added successfully")


async def delete(promo_code_id: uuid.UUID, vendor: Vendor) -> None:
    check_code = await models.ProductPromoCode.get_or_none(
        id=promo_code_id, vendor=vendor
    )
    if not check_code:
        raise exceptions.NotFoundError("Product promo code does not exist")
    await check_code.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def delete_product_from_promo_code(
    data_in: schemas.IProductPromoCodeRemoveIn, vendor: Vendor
) -> IResponseMessage:
    check_code = await models.ProductPromoCode.get_or_none(
        id=data_in.promo_code_id, vendor=vendor
    )
    if not check_code:
        raise exceptions.NotFoundError("Product promo code does not exist")
    get_products = await Product.filter(
        id__in=data_in.products, vendor=vendor
    ).all()
    await check_code.products.remove(*get_products)
    return IResponseMessage(message="products was successfully removed")
