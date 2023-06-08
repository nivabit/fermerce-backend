import uuid
from tortoise import fields, models

from enum import Enum


class DocumentEnum(str, Enum):
    identityNumber = "identityNumber"
    passportNumber = "passportNumber"
    businessRegistrationNumber = "businessRegistrationNumber"


class Recipient(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    bank_detail = fields.OneToOneField("models.BankDetail", related_name="recipient")
    recipient_code = fields.CharField(max_length=255)
    is_deleted = fields.BooleanField(default=False)
    vendor = fields.ForeignKeyField(
        "models.Vendor",
        related_name="payment_recipients",
        on_delete=fields.SET_NULL,
        null=True,
    )
    created_at = fields.DatetimeField(auto_now=True)
    updatedAt = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "fm_payment_recipient"


class BankDetail(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    type: str = fields.CharField(max_length=20, default="nuban")
    vendor = fields.OneToOneField("models.Vendor", related_name="bank_detail")
    currency = fields.CharField(max_length=10, default="NGN")
    bank_code = fields.CharField(max_length=10)
    account_number = fields.CharField(max_length=12)
    account_name = fields.CharField(max_length=255)
    verification: fields.BackwardOneToOneRelation["VendorVerification"]
    bvn = fields.CharField(max_length=20)
    is_verified = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now=True)
    updated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "fm_bank_detail"


class VendorVerification(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    vendor = fields.OneToOneField(
        "models.Vendor",
        related_name="verification",
        on_delete=fields.SET_NULL,
        null=True,
    )
    account = fields.OneToOneField(
        "models.BankDetail",
        related_name="verification",
        on_delete=fields.SET_NULL,
        null=True,
    )
    is_verified = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "fm_vendor_verification"
