import typing as t
import uuid
from fermerce.app.order.models import Order, OrderItem

from fermerce.app.warehouse.models import WereHouse
from fermerce.taskiq.broker import broker


@broker.task
async def add_order_to_warehouse_and_vendor(order_id: uuid.UUID):
    get_order = await Order.get_or_none(
        id=order_id,
    ).select_related(
        "shipping_address",
        "shipping_address__state",
    )
    if get_order:
        get_warehouse = await WereHouse.filter(
            state=get_order.shipping_address.state,
        ).first()
    if get_warehouse:
        await get_warehouse.orders.add(get_order)
    if get_order:
        get_order_items: t.List[OrderItem] = (
            OrderItem.filter(order=get_order)
            .select_related("product__vendor", "product")
            .all()
        )
        if get_order_items:
            if isinstance(get_order_items, list):
                for item in get_order_items:
                    await item.product.vendor.orders.add(order=item)
            await item.product.vendor.orders.add(order=item)
