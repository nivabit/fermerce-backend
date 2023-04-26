import uuid
from tortoise import fields, models


class ShippingAddress(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    street = fields.CharField(max_length=100)
    city = fields.CharField(max_length=100)
    phones = fields.CharField(max_length=100, null=True)
    state = fields.ForeignKeyField("models.State", related_name="shipping_address")
    zipcode = fields.CharField(max_length=10, null=True)
    user = fields.ForeignKeyField("models.User", related_name="shipping_address")
    created_at = fields.DatetimeField(auto_now_add=True)
