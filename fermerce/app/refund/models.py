import uuid
from tortoise import fields, models


class Refund(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    payment = fields.ForeignKeyField("models.Charge", related_name="refund")
    deducted_amount = fields.DecimalField(max_digits=12, decimal_places=2)
    merchant_note = fields.TextField(null=True, blank=True)
    customer_note = fields.TextField(null=True, blank=True)
    is_deleted = fields.BooleanField(default=False)
    fully_deducted = fields.BooleanField(default=False)
