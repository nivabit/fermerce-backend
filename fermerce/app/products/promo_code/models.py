import datetime
import uuid
from tortoise import fields, models

from fermerce.app.business.vendor.models import Vendor


class ProductPromoCode(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    code = fields.CharField(max_length=10)
    discount = fields.FloatField(null=False, default=10.0)
    single = fields.BooleanField(default=False)
    active_from = fields.DateField(
        null=True,
        default=datetime.datetime.utcnow,
    )
    active_to = fields.DateField(
        null=True,
        default=lambda: datetime.datetime.utcnow() + datetime.timedelta(5),
    )
    products = fields.ManyToManyField("models.Product", related_name="promo_codes")
    vendor: fields.ForeignKeyRelation[Vendor] = fields.ForeignKeyField(
        "models.Vendor", related_name="promo_codes"
    )
