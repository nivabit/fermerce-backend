from enum import Enum
from edgy import fields, Model

from fermerce.core.model.base_model import BaseModel


class DocumentEnum(str, Enum):
    identityNumber = "identityNumber"
    passportNumber = "passportNumber"
    businessRegistrationNumber = "businessRegistrationNumber"


class Recipient(BaseModel):
    bank_detail = fields.OneToOneField("BankDetail", related_name="recipient")
    recipient_code = fields.CharField(max_length=255)
    is_deleted = fields.BooleanField(default=False)
    vendor = fields.ForeignKey(
        "Vendor",
        related_name="payment_recipients",
        on_delete=fields.SET_NULL,
        null=True,
    )


class BankDetail(BaseModel):
    type: str = fields.CharField(max_length=20, default="nuban")
    vendor = fields.OneToOneField("Vendor", related_name="bank_detail")
    currency = fields.CharField(max_length=10, default="NGN")
    bank_code = fields.CharField(max_length=10)
    account_number = fields.CharField(max_length=12)
    account_name = fields.CharField(max_length=255)
    bvn = fields.CharField(max_length=20)
    is_verified = fields.BooleanField(default=False)


class VendorVerification(Model):
    vendor = fields.OneToOneField(
        "Vendor",
        related_name="verification",
        on_delete=fields.SET_NULL,
        null=True,
    )
    account = fields.OneToOneField(
        "BankDetail",
        related_name="verification",
        on_delete=fields.SET_NULL,
        null=True,
    )
    is_verified = fields.BooleanField(default=False)
