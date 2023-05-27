import uuid
from tortoise import fields, models
from fermerce.lib.utils.random_string import generate_orderId


class Payment(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    reference = fields.CharField(max_length=20, default=lambda: generate_orderId(15))
    flwRef = fields.CharField(max_length=70, default=None, null=True)
    total = fields.DecimalField(decimal_places=2, max_digits=12)
    user = fields.ForeignKeyField("models.User", related_name="payments")
    status = fields.ForeignKeyField("models.Status")
    order = fields.OneToOneField("models.Order", related_name="payment")
    refund_meta = fields.JSONField(null=True, blank=True)


class PaymentRecipient(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    type = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255)
    currency = fields.CharField(max_length=5, default="NGN")
    account_number = fields.CharField(max_length=255)
    bank_code = fields.CharField(max_length=255)
    currency = fields.CharField(max_length=255)
    recipient_code = fields.CharField(max_length=255)
    is_deleted = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now=True)
    updatedAt = fields.DatetimeField(auto_now_add=True)


class TransferPayment(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    amount = fields.IntField()
    currency = fields.CharField(max_length=255)
    source = fields.CharField(max_length=255)
    reason = fields.TextField(blank=True, null=True)
    recipient = fields.ForeignKeyField(
        "models.PaymentRecipient", related_name="transfer_payments"
    )
    status = fields.CharField(max_length=255)
    transfer_code = fields.CharField(max_length=255)
    createdAt = fields.DatetimeField(auto_now=True)
    updatedAt = fields.DatetimeField(auto_now_add=True)
