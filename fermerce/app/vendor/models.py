import uuid
from tortoise import fields, models
from fermerce.app.order.models import OrderItem
from fermerce.app.charge.models import TransferPayment
from fermerce.app.recipient.models import VendorVerification
from fermerce.lib.utils.password_hasher import Hasher


class Vendor(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    email = fields.CharField(max_length=50, null=True)
    password = fields.CharField(max_length=255, null=True)
    business_name = fields.CharField(max_length=30, null=False)
    logo = fields.ForeignKeyField("models.Media", null=True)
    phone_number = fields.CharField(max_length=20, default=None)
    address = fields.ForeignKeyField(
        "models.Address",
        related_name="vendor",
    )
    rating = fields.FloatField(default=0.0, null=True)
    verification: fields.BackwardOneToOneRelation["VendorVerification"]
    payments: fields.ManyToManyRelation[
        TransferPayment
    ] = fields.ManyToManyField(
        "models.TransferPayment",
        related_name="payouts",
        through="fm_vendor_payout",
    )
    reset_token = fields.CharField(max_length=255, null=True)
    is_suspended = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)
    is_verified = fields.BooleanField(default=False)
    is_archived = fields.BooleanField(default=False)
    orders: fields.ManyToManyRelation[OrderItem] = fields.ManyToManyField(
        "models.OrderItem",
        related_name="vendors",
        through="fm_vendor_orders",
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "fm_vendor"
        ordering = ("-id", "-created_at", "-modified_at")

    @staticmethod
    def generate_hash(password: str) -> str:
        return Hasher.hash_password(password)

    def check_password(self, plain_password: str) -> bool:
        check_pass = Hasher.check_password(plain_password, self.password)
        if check_pass:
            return True
        return False


class VendorSetting(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    vendor = fields.OneToOneField(
        "models.Vendor",
        related_name="setting",
    )
    return_policy = fields.TextField(default=None)
    receive_on_order = fields.BooleanField(default=True)
    receive_on_add_to_cart = fields.BooleanField(default=False)
    day_to_pay = fields.DatetimeField(auto_now=True)
    modified_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "fm_vendor_setting"
