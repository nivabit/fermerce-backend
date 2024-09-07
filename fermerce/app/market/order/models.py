from edgy import fields
from fermerce.core.model.base_model import BaseModel
from fermerce.lib.utils.random_string import (
    generate_order_Tracking_id,
    generate_orderId,
)


class Order(BaseModel):
    order_id = fields.CharField(
        max_length=15,
        default=lambda: str(generate_orderId(8)),
        index=True,
        unique=True,
    )
    user = fields.ForeignKey("models.User", related_name="orders")
    shipping_address = fields.ForeignKey("models.Address", related_name="orders")
    meta = fields.JSONField(null=True, blank=True)
    delivery_mode = fields.ForeignKey("models.DeliveryMode")
    is_complete = fields.BooleanField(default=False)


class OrderItem(BaseModel):
    tracking_id = fields.CharField(
        max_length=15,
        default=lambda: str(generate_order_Tracking_id(8)),
        index=True,
    )
    status = fields.ForeignKey("Status")
    product = fields.ForeignKey("Product")
    quantity = fields.IntegerField(default=1, null=False)
    promo_codes = fields.ManyToManyField(
        "ProductPromoCode", through="fm_order_item_promo_code"
    )
    order = fields.ForeignKey("Order", related_name="order_items")
    selling_unit = fields.ForeignKey("ProductSellingUnit")
