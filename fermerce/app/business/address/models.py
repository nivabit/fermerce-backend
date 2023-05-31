import uuid
from tortoise import fields, models
from fermerce.app.business.vendor.models import Vendor

from fermerce.app.users.user.models import User


class Address(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    street = fields.CharField(max_length=100)
    city = fields.CharField(max_length=100)
    phones = fields.CharField(max_length=100, null=True)
    state = fields.ForeignKeyField("models.State", related_name="address")
    user: fields.ForeignKeyRelation[User]
    vendor: fields.ForeignKeyRelation[Vendor]
    zipcode = fields.CharField(max_length=10, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "fm_address"
        ordering = ("street", "city", "-created_at")
