import uuid
import typing as t
from fastapi import status
from tortoise.expressions import Q
from fermerce.app.products.product.models import Product
from fermerce.app.users.user.models import User
from fermerce.core.schemas.response import IResponseMessage, ITotalCount
from fermerce.lib.errors import error
from fermerce.app.products.promo_code import models, schemas
from fastapi import Response


async def create(data_in: schemas.IProductPromoCodeIn, user: User) -> models.ProductPromoCode:
    check_code = await models.ProductPromoCode.get_or_none(code=data_in.code, vendor=user.vendor)
    if check_code:
        raise error.DuplicateError("product promo code already exists")
    new_code = await models.ProductPromoCode.create(**data_in.dict(), vendor=user.vendor)
    if new_code:
        return new_code
    raise error.ServerError("Internal server error")


async def get_promo_code_products(
    promo_code_id: uuid.UUID,
    user: User,
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
) -> Product:
    result = await models.ProductPromoCode.get_or_none(pk=promo_code_id, vendor=user.vendor)
    if not result:
        raise error.NotFoundError("Product promo code not found")
    offset = (page - 1) * per_page
    limit = per_page
    if filter_string:
        result = (
            result.products.filter(
                Q(name__icontains=filter_string) | Q(description__icontains=filter_string),
                vendor=user.vendor,
            )
            .all()
            .offset(offset)
            .limit(limit)
        )
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (offset + limit) < len(result) else None
    return {
        "previous": prev_page,
        "next": next_page,
        "total_results": len(result),
        "results": result,
    }


async def get(promo_code_id: uuid.UUID, user: User) -> models.ProductPromoCode:
    code = await models.ProductPromoCode.get_or_none(id=promo_code_id, vendor=user.vendor)
    if not code:
        raise error.NotFoundError("Product promo code not found")
    return code


async def filter(
    filter_string: str,
    user: User,
    per_page: int = 10,
    page: int = 0,
) -> t.List[models.ProductPromoCode]:
    offset = (page - 1) * per_page
    limit = per_page
    query = await models.ProductPromoCode
    if filter_string:
        query = query.filter(code__icontains=filter_string, vendor=user.vendor)

    results = await query.all().offset(offset).limit(limit)
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (offset + limit) < len(results) else None
    return {
        "previous": prev_page,
        "next": next_page,
        "total_results": len(results),
        "results": results,
    }


async def get_total_count(user: User) -> ITotalCount:
    total = await models.ProductPromoCode.filter(vendor=user.vendor).all().count()
    return ITotalCount(count=total).dict()


async def update(
    promo_code_id: uuid.UUID, data_in: schemas.IProductPromoCodeIn, user: User
) -> models.ProductPromoCode:
    get_promo_code = await models.ProductPromoCode.get_or_none(id=promo_code_id, vendor=user.vendor)
    if not get_promo_code:
        raise error.NotFoundError("promo code does not exist")
    check_code = await models.ProductPromoCode.get_or_none(code=data_in.code, vendor=user.vendor)
    if check_code and check_code.id != get_promo_code.id:
        raise error.DuplicateError("promo code already exists")
    else:
        await check_code.update_from_dict(data_in.dict())
        return check_code


async def add_product_to_promo_code(
    data_in: schemas.IProductPromoCodeUpdateIn, user: User
) -> IResponseMessage:
    get_promo_code = await models.ProductPromoCode.get_or_none(
        id=data_in.promo_code_id, vendor=user.vendor
    )
    if not get_promo_code:
        raise error.NotFoundError("promo code does not exist")
    check_products = await Product.filter(id__in=data_in.products, vendor=user.vendor).all()
    if not check_products:
        raise error.NotFoundError("No product is found")
    existing_promo_products = await get_promo_code.products.all()
    for index, product in enumerate(check_products):
        if product in existing_promo_products:
            check_products.pop(index)
    await get_promo_code.products.add(*check_products)
    return IResponseMessage(message="Product/products was added successfully")


async def delete(promo_code_id: uuid.UUID, user: User) -> None:
    check_code = await models.ProductPromoCode.get_or_none(id=promo_code_id, vendor=user.vendor)
    if not check_code:
        raise error.NotFoundError("Product promo code does not exist")
    await check_code.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def delete_product_from_promo_code(
    data_in: schemas.IProductPromoCodeRemoveIn, user: User
) -> IResponseMessage:
    check_code = await models.ProductPromoCode.get_or_none(
        id=data_in.promo_code_id, vendor=user.vendor
    )
    if not check_code:
        raise error.NotFoundError("Product promo code does not exist")
    get_products = await Product.filter(id__in=data_in.products, vendor=user.vendor).all()
    await check_code.products.remove(*get_products)
    return IResponseMessage("products was successfully removed")
