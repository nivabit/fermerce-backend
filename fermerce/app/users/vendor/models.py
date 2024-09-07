import uuid
from tortoise import fields, models
from fermerce.lib.utils.password_hasher import Hasher


class Vendor(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    email = fields.CharField(max_length=50, null=True)
    password = fields.CharField(max_length=255, null=True)
    business_name = fields.CharField(max_length=30, null=False)
    logo = fields.ForeignKey("models.Media", null=True)
    phone_number = fields.CharField(max_length=20, default=None)
    address = fields.ManyToManyField(
        "models.Address",
        through="fm_business_address",
        related_name="vendors",
    )
    rating = fields.FloatField(default=0.0, null=True)
    payments = fields.ManyToManyField(
        "models.TransferPayment",
        related_name="payouts",
        through="fm_vendor_payout",
    )
    reset_token = fields.CharField(max_length=255, null=True)
    is_suspended = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)
    is_verified = fields.BooleanField(default=False)
    is_archived = fields.BooleanField(default=False)
    orders = fields.ManyToManyField(
        "models.OrderItem",
        related_name="vendors",
        through="fm_vendor_orders",
    )
    created_at = fields.DateTimeField(auto_now_add=True)
    modified_at = fields.DateTimeField(auto_now=True)

    class Meta:
        tablename = "fm_vendor"
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
    day_to_pay = fields.DateTimeField(auto_now=True)
    modified_at = fields.DateTimeField(auto_now=True)
    created_at = fields.DateTimeField(auto_now_add=True)
    modified_at = fields.DateTimeField(auto_now=True)

    class Meta:
        tablename = "fm_vendor_setting"
