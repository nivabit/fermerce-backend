import datetime
from edgy import fields
from fermerce.core.model.base_model import BaseModel


class ProductPromoCode(BaseModel):
    code = fields.CharField(max_length=10)
    discount = fields.FloatField(null=False, default=0.1)
    single = fields.BooleanField(default=False)
    active_from = fields.DateField(
        null=True,
        default=datetime.datetime.now(datetime.UTC).date,
    )
    active_to = fields.DateField(
        null=True,
        default=lambda: datetime.datetime.now(datetime.UTC).date()
        + datetime.timedelta(7),
    )
    products = fields.ManyToManyField(
        "Product",
        related_name="promo_codes",
        through="fm_product_promo_codes",
    )
    vendor = fields.ForeignKey("Vendor", related_name="promo_codes")
