from enum import Enum
import uuid
from tortoise import fields, models
from fermerce.lib.utils.random_string import generate_orderId


class DocumentEnum(str, Enum):
    identityNumber = "identityNumber"
    passportNumber = "passportNumber"
    businessRegistrationNumber = "businessRegistrationNumber"


class Payment(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    reference = fields.CharField(max_length=20, default=lambda: generate_orderId(15))
    total = fields.DecimalField(decimal_places=2, max_digits=12)
    user = fields.ForeignKeyField("models.User", related_name="payments")
    status = fields.ForeignKeyField("models.Status")
    order = fields.OneToOneField("models.Order", related_name="payment")
    refund_meta = fields.JSONField(null=True, blank=True)

    class Meta:
        table = "fm_payment"

    @staticmethod
    def generate_order_reference():
        return generate_orderId(15)


class BankDetail(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    bank_code = fields.CharField(max_length=10)
    country_code = fields.CharField(max_length=10)
    account_number = fields.CharField(max_length=12)
    account_name = fields.CharField(max_length=255)
    account_type = fields.CharField(max_length=100)
    document_type = fields.CharEnumField(
        DocumentEnum,
        "bank verification document type",
        max_length=30,
        default=DocumentEnum.identityNumber,
    )
    document_number = fields.CharField(max_length=40)

    class Meta:
        table = "fm_bank_detail"


class SaveCard(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="payment_cards")
    authorization_code = fields.CharField(max_length=100, null=False)
    bin = fields.CharField(max_length=8, null=False)
    last4 = fields.CharField(max_length=8, null=False)
    exp_month = fields.CharField(max_length=4)
    exp_year = fields.CharField(max_length=4)
    card_type = fields.CharField(max_length=20)
    bank = fields.CharField(max_length=100)
    country_code = fields.CharField(max_length=20)
    brand = fields.CharField(max_length=20)
    reusable = fields.BooleanField(default=False)
    created = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "fm_save_payment_card"


class PaymentRecipient(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    currency = fields.CharField(max_length=5, default="NGN")
    status = fields.ForeignKeyField("models.Status")
    bank_details = fields.ForeignKeyField("models.BankDetail", related_name="payments")
    currency = fields.CharField(max_length=255)
    recipient_code = fields.CharField(max_length=255)
    is_deleted = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now=True)
    updatedAt = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "fm_payment_recipient"


class TransferPayment(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    amount = fields.IntField()
    currency = fields.CharField(max_length=255)
    source = fields.CharField(max_length=255)
    reason = fields.TextField(blank=True, null=True)
    recipient = fields.ForeignKeyField(
        "models.PaymentRecipient",
        related_name="transfer_payments",
    )
    status = fields.CharField(max_length=255)
    transfer_code = fields.CharField(max_length=255)
    status = fields.ForeignKeyField("models.Status")
    createdAt = fields.DatetimeField(auto_now=True)
    updatedAt = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "fm_transfer_payment"
