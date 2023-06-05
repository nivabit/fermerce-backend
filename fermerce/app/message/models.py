import uuid
from tortoise import models, fields


class Message(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    vendor = fields.ForeignKeyField("models.Vendor", related_name="messages")
    sender = fields.ForeignKeyField(
        "models.Staff", related_name="messages", null=True
    )
    message = fields.CharField(max_length=300)
    created_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "fm_message"
