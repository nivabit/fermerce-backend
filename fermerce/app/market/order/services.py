import datetime
import typing as t
import uuid
from tortoise.expressions import Q
from fermerce.app.cart.models import Cart
from fermerce.app.promo_code.models import ProductPromoCode
from fermerce.app.delivery_mode.models import DeliveryMode
from fermerce.app.status.models import Status
from fermerce.app.address.models import Address
from fermerce.app.user.models import User
from fermerce.app.order import models, schemas
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage
from fermerce.core.services.base_old import filter_and_list, filter_and_single
from fermerce.lib.exceptions import exceptions
from fermerce.taskiq.warehouse.tasks import add_order_to_warehouse_and_vendor


async def create(
    data_in: schemas.IOrderIn,
    user: User,
) -> schemas.IOrderSuccessOut:
    get_shipping_address = await Address.get_or_none(id=data_in.address_id)
    if not get_shipping_address:
        raise exceptions.NotFoundError("Shipping shipping_address does not exist")
    get_delivery_mode = await DeliveryMode.get_or_none(id=data_in.delivery_mode)
    if not get_delivery_mode:
        raise exceptions.NotFoundError("Order delivery mode not found")
    get_carts = (
        await Cart.filter(user=user, id__in=data_in.cart_ids)
        .prefetch_related("product", "selling_unit")
        .all()
    )
    if not get_carts:
        raise exceptions.NotFoundError(
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
                await add_order_to_warehouse_and_vendor(order_id=new_order.id)
                deleted_count = await Cart.filter(
                    user=user, id__in=data_in.cart_ids
                ).delete()
                if deleted_count == len(get_carts):
                    return schemas.IOrderSuccessOut(order_id=new_order.id)
    raise exceptions.ServerError("Error creating order, please try again")


async def update_order_status(data_in: schemas.IOrderUpdate) -> dict:
    try:
        get_user_order_item = await models.OrderItem.get_or_none(
            tracking_id=data_in.tracking_id
        )
        if not get_user_order_item:
            raise exceptions.NotFoundError("Order item is not found")
        get_status = await Status.get_or_none(id=data_in.status_id)
        if not get_status:
            raise exceptions.NotFoundError("Status is not found")
        get_user_order_item.status = get_status
        await get_user_order_item.save()
        return IResponseMessage(message="Order status updated successfully")
    except:
        raise exceptions.ServerError("Error updating order status, please try again")


async def add_promo_code(
    data_in: schemas.IOrderUpdatePromoCodeIn, user: User
) -> IResponseMessage:
    get_order_items = (
        await models.OrderItem.filter(order__id=data_in.order_id, order__user=user)
        .select_related("product__vendor", "product", "product__promo_codes")
        .all()
    )
    if not get_order_items:
        raise exceptions.NotFoundError("Order not found")
    promo_code = await ProductPromoCode.get_or_none(
        code=data_in.promo_code,
        active_from__lte=datetime.datetime.utcnow().date(),
        active_to__gte=datetime.datetime.utcnow().date(),
    ).select_related("vendor", "products")
    if not promo_code:
        raise exceptions.BadDataError("Invalid promo code")
    promo_codes_product = await promo_code.products.all()
    for item in get_order_items:
        if isinstance(promo_code.products, list):
            if item.product in promo_codes_product:
                if not promo_code in await item.promo_codes.all():
                    await item.promo_codes.add(promo_code)
        if item.product == promo_code.products:
            if not promo_code in await item.promo_codes.all():
                await item.promo_codes.add(promo_code)
        if promo_code.vendor == item.product.vendor and promo_code.single == False:
            if isinstance(promo_code.products, list):
                if not promo_code in promo_codes_product:
                    await item.promo_codes.add(promo_code)
            if item.product == promo_code.products:
                if not promo_code in promo_codes_product:
                    await item.promo_codes.add(promo_code)
        return IResponseMessage(message="promo code was applied successfully")
    raise exceptions.BadDataError("Invalid promo code")


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
    raise exceptions.NotFoundError("order not found")


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
    raise exceptions.NotFoundError("order items not found")
