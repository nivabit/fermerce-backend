import datetime
import typing as t
import uuid
from tortoise.expressions import Q
from fermerce.app.markets.cart.models import Cart
from fermerce.app.products.promo_code.models import ProductPromoCode
from fermerce.app.markets.delivery_mode.models import DeliveryMode
from fermerce.app.markets.status.models import Status
from fermerce.app.users.address.models import ShippingAddress
from fermerce.app.users.user.models import User
from fermerce.app.markets.order import models, schemas
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error


async def create(
    data_in: schemas.IOrderIn,
    user: User,
) -> schemas.IOrderSuccessOut:
    get_shipping_address = await ShippingAddress.get_or_none(id=data_in.address_id)
    if not get_shipping_address:
        raise error.NotFoundError("Shipping shipping_address does not exist")
    get_delivery_mode = await DeliveryMode.get_or_none(id=data_in.delivery_mode)
    if not get_delivery_mode:
        raise error.NotFoundError("Order delivery mode not found")
    get_carts = (
        await Cart.filter(user=user, id__in=data_in.cart_ids)
        .prefetch_related("product", "selling_unit")
        .all()
    )
    if not get_carts:
        raise error.NotFoundError(
            "No product in cart, please add product to cart to continue"
        )
    get_initial_status = await Status.get_or_none(name__icontains="pending")
    if not get_initial_status:
        get_initial_status = await Status.create(name="pending")

    new_order = await models.Order.create(
        user=user,
        shipping_address=get_shipping_address,
        delivery_mode=get_delivery_mode,
        is_completed=False,
    )

    if new_order:
        order_items_list = [
            models.OrderItem(
                status=get_initial_status,
                product=item.product,
                quantity=item.quantity,
                selling_unit=item.selling_unit,
                order=new_order,
            )
            for item in get_carts
        ]

        if order_items_list:
            results = await models.OrderItem.bulk_create(order_items_list)
            if results:
                deleted_count = await Cart.filter(
                    user=user, id__in=data_in.cart_ids
                ).delete()
                if deleted_count == len(get_carts):
                    return schemas.IOrderSuccessOut(order_id=new_order.id)
    raise error.ServerError("Error creating order, please try again")


async def update_order_status(data_in: schemas.IOrderUpdate) -> dict:
    try:
        get_user_order_item = await models.OrderItem.get_or_none(
            tracking_id=data_in.tracking_id
        )
        if not get_user_order_item:
            raise error.NotFoundError("Order item is not found")
        get_status = await Status.get_or_none(id=data_in.status_id)
        if not get_status:
            raise error.NotFoundError("Status is not found")
        get_user_order_item.status = get_status
        await get_user_order_item.save()
        return IResponseMessage(message="Order status updated successfully")
    except:
        raise error.ServerError("Error updating order status, please try again")


async def add_promo_code(
    data_in: schemas.IOrderUpdatePromoCodeIn, user: User
) -> IResponseMessage:
    get_item = await models.OrderItem.get_or_none(
        id=data_in.order_item_id, order__user=user
    ).select_related("product", "product__vendor")
    if not get_item:
        raise error.NotFoundError("Order item is not found")
    promo_code = await ProductPromoCode.get_or_none(
        code=data_in.promo_code,
        active_from__lte=datetime.datetime.utcnow().date(),
        active_to__gte=datetime.datetime.utcnow().date(),
    ).select_related("vendor")
    if not promo_code:
        raise error.NotFoundError("Promo code not found")
    if get_item.product.vendor.id == promo_code.vendor.id:
        if promo_code.single:
            if await get_item.promo_codes.filter(id=promo_code.id).exists():
                return IResponseMessage(message="promo code  has already bean applied")
            await get_item.promo_codes.add(promo_code)
            return IResponseMessage(message="Order status updated successfully")
        else:
            if await promo_code.products.filter(id=get_item.product.id).exists():
                if await get_item.promo_codes.filter(id=promo_code.id).exists():
                    return IResponseMessage(message="Order status updated successfully")
                await get_item.promo_codes.add(promo_code)
                return IResponseMessage(message="Order status updated successfully")
        raise error.BadDataError("Invalid promo code")
    raise error.BadDataError("Invalid promo code")


async def filter(
    user: User,
    filter_string: str = "",
    per_page: int = 10,
    page: int = 0,
    order_by: str = "id",
    sort_by: t.Optional[SortOrder] = SortOrder.asc,
    load_related: bool = False,
    select: str = "",
) -> models.Order:
    query = models.Order
    if user:
        query = query.filter(user=user)
    if filter_string:
        query = query.filter(Q(order_id__icontains=filter_string))
    result = await filter_and_list(
        model=models.Order,
        query=query,
        sort_by=sort_by,
        order_by=order_by,
        page=page,
        per_page=per_page,
        load_related=load_related,
        select=select,
    )
    return result


async def get_order(
    user: User,
    order_id: uuid.UUID,
    load_related: bool = False,
) -> models.Order:
    query = models.Order.filter(id=order_id, user=user)
    result = await filter_and_single(
        model=models.Order,
        query=query,
        load_related=load_related,
    )
    if result:
        return result
    raise error.NotFoundError("order not found")


async def get_order_items(
    user: User,
    order_id: uuid.UUID,
    load_related: bool = False,
    per_page: int = 10,
    page: int = 0,
) -> models.OrderItem:
    query = models.OrderItem.filter(order__user=user, order__id=order_id)
    results = await filter_and_list(
        model=models.OrderItem,
        query=query,
        load_related=load_related,
        page=page,
        per_page=per_page,
    )
    if results:
        return results
    raise error.NotFoundError("order items not found")
