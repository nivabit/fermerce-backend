from edgy import fields

from fermerce.core.model.base_model import BaseModel


class Refund(BaseModel):
    payment = fields.ForeignKey("models.Charge", related_name="refund")
    deducted_amount = fields.DecimalField(max_digits=12, decimal_places=2)
    merchant_note = fields.TextField(null=True, blank=True)
    customer_note = fields.TextField(null=True, blank=True)
    is_deleted = fields.BooleanField(default=False)
    fully_deducted = fields.BooleanField(default=False)
