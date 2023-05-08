import typing as t
import uuid
from fermerce.app.markets.cart.models import Cart
from fermerce.app.markets.delivery_mode.models import DeliveryMode
from fermerce.app.markets.status.models import Status
from fermerce.app.users.address.models import ShippingAddress
from fermerce.app.users.user.models import User
from fermerce.app.markets.order import models, schemas
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
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
    get_carts = await Cart.filter(user=user, id__in=data_in.cart_ids).all()
    if not get_carts:
        raise error.NotFoundError("No product in cart, please add product to cart to continue")
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
                deleted_count = Cart.filter(user=user, id__in=data_in.cart_ids).delete()
                if deleted_count == len(get_carts):
                    return schemas.IOrderSuccessOut(order_id=new_order.id)
    raise error.ServerError("Error creating order, please try again")


async def update_order_status(data_in: schemas.IOrderUpdate) -> dict:
    get_user_order_item = await models.OrderItem.get_or_none(tracking_id=data_in.tracking_id)
    if not get_user_order_item:
        raise error.NotFoundError("Order item is not found")
    get_status = await Status.get_or_none(id=data_in.status_id)
    if not get_status:
        raise error.NotFoundError("Status is not found")
    get_user_order_item.status = get_status
    result = await get_user_order_item.save()
    if result:
        return IResponseMessage(message="Order status updated successfully")
    raise error.ServerError("Error updating order status, please try again")


async def add_promo_code(data_in: schemas.IOrderUpdatePromoCodeIn) -> dict:
    get_user_order = await models.OrderItem.get_or_none(id=data_in.order_id).prefetch_related(
        "promo_codes", "items"
    )
    if not get_user_order:
        raise error.NotFoundError("Order item is not found")
    get_promo_codes = await Status.get_or_none(id=data_in.promo_code_id)
    if not get_promo_codes:
        raise error.NotFoundError("Status is not found")

    get_user_order_item.status = get_status
    result = await get_user_order_item.save()
    if result:
        return IResponseMessage(message="Order status updated successfully")
    raise error.ServerError("Error updating order status, please try again")


async def filter(
    user: User,
    filter_string: str = "",
    per_page: int = 10,
    page: int = 0,
    order_by: str = "id",
    sort_by: t.Optional[SortOrder] = SortOrder.asc,
    get_orders=models.Order,
) -> models.Order:
    if user:
        get_orders = models.Order.filter(user=user)
    if filter_string:
        get_orders = get_orders.filter(order_id__icontains=filter_string)
    if sort_by == SortOrder.asc:
        get_orders = get_orders.order_by(*[f"-{el}" for el in order_by.split(",")])
    else:
        get_orders = get_orders.order_by(*[el for el in order_by.split(",")])
    get_orders = get_orders.prefetch_related(
        *models.Order._meta.fk_fields, *models.Order._meta.backward_fk_fields
    )
    offset = (page - 1) * per_page
    limit = per_page
    results = await get_orders.all().offset(offset).limit(limit)

    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (offset + limit) < len(results) else None
    return {
        "previous": prev_page,
        "next": next_page,
        "total_results": len(results),
        "results": results,
    }


async def get_order(
    user: User,
    order_id: uuid.UUID,
) -> models.Order:
    order = await models.OrderItem.get_or_none(order_id=order_id, user=user).prefetch_related(
        *models.Order._meta.fk_fields,
        *models.Order._meta.backward_fk_fields,
    )
    if order:
        return order
    raise error.NotFoundError("order not found")


async def get_order_items(
    user: User,
    order_id: str,
) -> models.Order:
    order = await models.OrderItem.filter(order__id=order_id, user=user).prefetch_related(
        *models.OrderItem._meta.fk_fields, *models.OrderItem._meta.backward_fk_fields
    )
    if order:
        return order.items
    raise error.NotFoundError("order not found")
