import uuid
from tortoise import models, fields


class Tracking(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    order_item = fields.ForeignKeyField("models.OrderItem", related_name="trackings")
    location = fields.CharField(max_length=300, null=True, blank=True)
    note = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "fm_tracking"
