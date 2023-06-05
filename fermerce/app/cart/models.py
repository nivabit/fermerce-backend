import uuid
from tortoise import fields, models


from fermerce.app.selling_units.models import ProductSellingUnit


class Cart(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    product = fields.ForeignKeyField("models.Product")
    quantity = fields.IntField(default=0, null=False)
    user = fields.ForeignKeyField("models.User", related_name="carts")
    selling_unit: fields.ForeignKeyRelation[
        ProductSellingUnit
    ] = fields.ForeignKeyField("models.ProductSellingUnit")
    created_at: fields.DatetimeField(auto_now=True)

    class Meta:
        table = "fm_cart"
