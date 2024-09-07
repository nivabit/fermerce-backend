from edgy import fields

from fermerce.core.model.base_model import BaseModel


class TransferPayment(BaseModel):
    amount = fields.IntegerField()
    currency = fields.CharField(max_length=255)
    source = fields.CharField(max_length=255)
    reason = fields.TextField(blank=True, null=True)
    recipient = fields.ForeignKey(
        "Recipient",
        related_name="transfer_payments",
    )
    transfer_code = fields.CharField(max_length=255)
    status = fields.ForeignKey("Status", related_name=None)
