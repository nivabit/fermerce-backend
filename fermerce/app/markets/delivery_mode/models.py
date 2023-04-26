import uuid
from tortoise import fields, models


class DeliveryMode(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    price = fields.DecimalField(max_digits=12, decimal_places=2)
    name = fields.CharField(max_length=50, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
