import uuid
from tortoise import fields, models
from fermerce.lib.utils.random_string import generate_orderId


class Charge(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    reference = fields.CharField(
        max_length=20, default=lambda: generate_orderId(15)
    )
    total = fields.DecimalField(decimal_places=2, max_digits=12)
    user = fields.ForeignKeyField("models.User", related_name="payments")
    status = fields.ForeignKeyField("models.Status")
    order = fields.OneToOneField("models.Order", related_name="payment")

    class Meta:
        table = "fm_payment"

    @staticmethod
    def generate_order_reference():
        return generate_orderId(15)


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
