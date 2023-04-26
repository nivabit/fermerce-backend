import typing as t
import uuid
from fastapi import status, Response
from fermerce.app.markets.cart.models import Cart
from fermerce.app.products.selling_units.models import ProductSellingUnit
from fermerce.app.users.user.models import User
from fermerce.core.enum.sort_type import SortOrder
from fermerce.lib.errors import error
from fermerce.app.markets.cart import models, schemas
from fermerce.app.products.product.models import Product


async def create(data_in: schemas.ICartIn, user: User) -> models.Cart:
    get_product = await Product.get_or_none(id=data_in.product_id)
    if not get_product:
        raise error.NotFoundError("Product not found")
    selling_unit = await ProductSellingUnit.get_or_none(id=data_in.selling_unit)
    if not selling_unit:
        raise error.NotFoundError("Product selling unit not found")
    if selling_unit.size == 0:
        raise error.BadDataError("Product is out of stock")
    if selling_unit.size < data_in.quantity:
        raise error.BadDataError(
            f"only {selling_unit.size} of {get_product.name} left for this product"
        )
    else:
        selling_unit.update_from_dict(dict(size=selling_unit.size - data_in.quantity))
        await selling_unit.save()

    new_cart = await Cart.create(
        user=user,
        product=get_product,
        quantity=data_in.quantity,
        selling_unit=selling_unit,
    )
    if not new_cart:
        raise error.ServerError("Error add product to cart")
    return new_cart


async def update(
    data_in: schemas.ICartIn, user: User, cart_id: uuid.UUID
) -> models.Cart:
    get_cart = await Cart.get_or_none(id=cart_id, user=user)
    if not get_cart:
        raise error.NotFoundError("Cart not found")
    get_product = await Product.get_or_none(id=data_in.product_id)
    if not get_product:
        raise error.NotFoundError("Product not found")
    selling_unit = await ProductSellingUnit.get_or_none(id=data_in.selling_unit)
    if not selling_unit:
        raise error.NotFoundError("Product selling unit not found")
    if selling_unit.size == 0:
        raise error.BadDataError("Product is out of stock")
    if selling_unit.size < data_in.quantity:
        raise error.BadDataError(
            f"only {selling_unit.size} of {get_product.name} left for this product"
        )
    else:
        selling_unit.update_from_dict(dict(size=selling_unit.size - data_in.quantity))
        await selling_unit.save()

    get_cart.update_from_dict(quantity=data_in.quantity)
    try:
        await get_cart.save()
        return get_cart
    except:
        raise error.ServerError("Error add product to cart")


async def get(cart_id: uuid.UUID, user: User) -> models.Cart:
    get_cart = await Cart.get_or_none(id=cart_id, user=user)
    if not get_cart:
        raise error.NotFoundError("Cart not found")
    return get_cart


async def filter(
    user: User,
    filter_string: str = None,
    per_page: int = 10,
    page: int = 0,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = "-id",
) -> t.List[models.Cart]:
    query = Cart.filter(user=user)
    if filter_string:
        query = query.filter(product__name__icontains=filter_string)
    set_sort_by = []
    if sort_by == SortOrder.asc and order_by:
        for el in order_by.split(","):
            if hasattr(Cart, el):
                set_sort_by.append(f"-{el}")
    else:
        for el in order_by.split(","):
            if hasattr(Cart, el):
                set_sort_by.append(f"{el}")
    if set_sort_by:
        query = query.order_by(*set_sort_by)
    results = await query.all().offset(offset).limit(limit)
    offset = (page - 1) * per_page
    limit = per_page
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (offset + limit) < len(results) else None
    return {
        "previous": prev_page,
        "next": next_page,
        "total_results": len(results),
        "results": results,
    }


async def delete(cart_id: uuid.UUID, user: User):
    get_cart = await Cart.get_or_none(id=cart_id, user=user)
    if not get_cart:
        raise error.NotFoundError("Cart not found")
    get_selling_unit = await ProductSellingUnit.get_or_none(id=get_cart.selling_unit.id)
    if get_selling_unit:
        get_selling_unit.update_from_dict(size=get_cart.quantity)
        await get_selling_unit.save()
    await get_cart.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
