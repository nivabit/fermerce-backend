import typing as t
import uuid
from fastapi import status, Response
from tortoise.expressions import Q
from fermerce.app.selling_units.models import ProductSellingUnit
from fermerce.app.user.models import User
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.services.base_old import filter_and_list, filter_and_single
from fermerce.lib.exceptions import exceptions
from fermerce.app.wishlist import models, schemas
from fermerce.app.product.models import Product


async def create(data_in: schemas.IWishListIn, user: User) -> models.WishList:
    get_product = await Product.get_or_none(id=data_in.product_id)
    if not get_product:
        raise exceptions.NotFoundError("Product not found")
    selling_unit = await ProductSellingUnit.get_or_none(id=data_in.selling_unit)
    if not selling_unit:
        raise exceptions.NotFoundError("Product selling unit not found")
    if selling_unit.size == 0:
        raise exceptions.BadDataError("Product is out of stock")
    if selling_unit.size < data_in.quantity:
        raise exceptions.BadDataError(
            f"only {selling_unit.size} of {get_product.name} left for this product"
        )

    new_wish_list = await models.WishList.create(
        user=user,
        product=get_product,
        quantity=data_in.quantity,
        selling_unit=selling_unit,
    )
    if not new_wish_list:
        raise exceptions.ServerError("Error add product to wish list")
    return new_wish_list


async def update(
    data_in: schemas.IWishListIn, user: User, wish_item_id: uuid.UUID
) -> models.WishList:
    get_wish_list = await models.WishList.get_or_none(id=wish_item_id, user=user)
    if not get_wish_list:
        raise exceptions.NotFoundError("wish list item not found")
    get_product = await Product.get_or_none(id=data_in.product_id)
    if not get_product:
        raise exceptions.NotFoundError("Product not found")
    selling_unit = await ProductSellingUnit.get_or_none(id=data_in.selling_unit)
    if not selling_unit:
        raise exceptions.NotFoundError("Product selling unit not found")
    if selling_unit.size == 0:
        await Product.filter(id=data_in.product_id).update(in_stock=False)
        raise exceptions.BadDataError("Product is out of stock")
    if selling_unit != get_wish_list.selling_unit:
        if (
            selling_unit.size < get_wish_list.quantity
            or selling_unit.size < data_in.quantity
        ):
            raise exceptions.BadDataError(
                f"only {selling_unit.size} quantity of {get_product.name} left for this product"
            )

    get_wish_list.update_from_dict(dict(quantity=data_in.quantity))
    try:
        await get_wish_list.save()
        return get_wish_list
    except:
        raise exceptions.ServerError("Error add product to wish list")


async def get(
    wish_item_id: uuid.UUID,
    user: User,
    load_related: bool = False,
) -> models.WishList:
    query = models.WishList.filter(id=wish_item_id, user=user)
    result = await filter_and_single(
        model=models.WishList,
        query=query,
        load_related=load_related,
    )
    if not result:
        raise exceptions.NotFoundError("wish list item not found")
    return result


async def filter(
    user: User,
    filter_string: str = None,
    per_page: int = 10,
    page: int = 0,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = "id",
    load_related: bool = False,
    select: str = "",
) -> t.List[models.WishList]:
    query = models.WishList.filter(user=user)
    if filter_string:
        query = query.filter(Q(product__name__icontains=filter_string))
    results = await filter_and_list(
        model=models.WishList,
        query=query,
        per_page=per_page,
        page=page,
        sort_by=sort_by,
        order_by=order_by,
        load_related=load_related,
        select=select,
    )

    return results


async def delete(wish_item_id: uuid.UUID, user: User):
    get_wish_list = await models.WishList.get_or_none(id=wish_item_id, user=user)
    if not get_wish_list:
        raise exceptions.NotFoundError("wish list not found")
    await get_wish_list.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
