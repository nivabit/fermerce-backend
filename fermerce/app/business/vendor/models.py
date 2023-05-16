import uuid
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from fermerce.app.markets.country.models import Country
from fermerce.app.markets.order.models import OrderItem
from fermerce.app.markets.state.models import State

from fermerce.app.users.user.models import User


class Vendor(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    business_name = fields.CharField(max_length=30, null=False)
    logo = fields.ForeignKeyField("models.Media", null=True)
    states: fields.ManyToManyRelation[State] = fields.ManyToManyField(
        "models.State"
    )
    user: fields.ForeignKeyRelation[User] = fields.OneToOneField(
        "models.User", related_name="vendor"
    )
    rating = fields.FloatField(default=0.0, null=True)
    countries: fields.ManyToManyRelation[Country] = fields.ManyToManyField(
        "models.Country"
    )
    is_suspended = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)
    is_archived = fields.BooleanField(default=False)
    orders: fields.ManyToManyRelation[OrderItem] = fields.ManyToManyField(
        "models.OrderItem", "vendor_order"
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        ordering = ("-id", "-created_at", "-modified_at")


UserOut = pydantic_model_creator(Vendor, name="vendor")
