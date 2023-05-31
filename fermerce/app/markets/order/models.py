import uuid
from tortoise import fields, models
from fermerce.app.payment.models import Payment
from fermerce.app.markets.tracking.models import Tracking
from fermerce.lib.utils.random_string import (
    generate_order_Tracking_id,
    generate_orderId,
)


class Order(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    order_id = fields.CharField(
        max_length=15,
        default=lambda: str(generate_orderId(8)),
        index=True,
        unique=True,
    )
    user = fields.ForeignKeyField("models.User", related_name="orders")
    shipping_address = fields.ForeignKeyField("models.Address", related_name="orders")
    payment: fields.BackwardOneToOneRelation[Payment]
    delivery_mode = fields.ForeignKeyField("models.DeliveryMode")
    is_complete = fields.BooleanField(default=False)
    items: fields.ForeignKeyRelation["OrderItem"]

    class Meta:
        table = "fm_order"


class OrderItem(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    tracking_id = fields.CharField(
        max_length=15,
        default=lambda: str(generate_order_Tracking_id(8)),
        index=True,
    )
    status = fields.ForeignKeyField("models.Status")
    product = fields.ForeignKeyField("models.Product")
    quantity = fields.IntField(default=1, null=False)
    promo_codes = fields.ManyToManyField(
        "models.ProductPromoCode", through="fm_order_item_promo_code"
    )
    order = fields.ForeignKeyField("models.Order", related_name="order_items")
    trackings: fields.ReverseRelation[Tracking]
    selling_unit = fields.ForeignKeyField("models.ProductSellingUnit")
    created_at: fields.DatetimeField(auto_now=True)

    class Meta:
        table = "fm_order_item"
