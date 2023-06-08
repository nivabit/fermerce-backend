import uuid
from tortoise import fields, models
from fermerce.app.user.models import User
from fermerce.app.vendor.models import Vendor


class Address(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    street = fields.CharField(max_length=100)
    city = fields.CharField(max_length=100)
    phones = fields.CharField(max_length=100, null=True)
    state = fields.ForeignKeyField("models.State", related_name="address")
    users: fields.ManyToManyRelation[User]
    vendors: fields.ManyToManyRelation[Vendor]
    zipcode = fields.CharField(max_length=10, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "fm_address"
        ordering = ("street", "city", "-created_at")
