import uuid
from tortoise import fields, models


class TransferPayment(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    amount = fields.IntField()
    currency = fields.CharField(max_length=255)
    source = fields.CharField(max_length=255)
    reason = fields.TextField(blank=True, null=True)
    recipient = fields.ForeignKeyField(
        "models.Recipient",
        related_name="transfer_payments",
    )
    status = fields.CharField(max_length=255)
    transfer_code = fields.CharField(max_length=255)
    status = fields.ForeignKeyField("models.Status")
    createdAt = fields.DatetimeField(auto_now=True)
    updatedAt = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "fm_transfer_payment"
