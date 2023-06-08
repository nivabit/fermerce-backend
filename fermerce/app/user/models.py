import uuid
from tortoise import fields, models
from fermerce.app.cart.models import Cart
from fermerce.app.order.models import Order
from fermerce.app.auth.models import Auth
from fermerce.lib.utils.password_hasher import Hasher
from fermerce.app.staff.models import Staff


class User(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4())
    username = fields.CharField(max_length=20, unique=True)
    firstname = fields.CharField(max_length=50, null=True)
    lastname = fields.CharField(max_length=50, null=True, unique=True, index=True)
    email = fields.CharField(max_length=70, null=False, unique=True, index=True)
    password = fields.CharField(max_length=255, null=True)
    is_verified = fields.BooleanField(default=False, null=True)
    is_suspended = fields.BooleanField(default=False, null=True)
    is_active = fields.BooleanField(default=False, null=True)
    is_archived = fields.BooleanField(default=False, null=True)
    reset_token = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    staff: fields.ReverseRelation[Staff]
    auths: fields.ReverseRelation[Auth]
    shipping_address = fields.ManyToManyField(
        "models.Address",
        through="fm_shipping_address",
        related_name="users",
    )
    carts = fields.ReverseRelation[Cart]
    orders = fields.ReverseRelation[Order]

    class Meta:
        table = "fm_user"
        ordering = ("-created_at", "-id")

    @staticmethod
    def generate_hash(password: str) -> str:
        return Hasher.hash_password(password)

    def check_password(self, plain_password: str) -> bool:
        check_pass = Hasher.check_password(plain_password, self.password)
        if check_pass:
            return True
        return False
