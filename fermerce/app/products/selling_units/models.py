import uuid
from tortoise import models, fields


class ProductSellingUnit(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    unit = fields.ForeignKeyField("models.MeasuringUnit")
    size = fields.IntField(null=False, default=5)
    price = fields.DecimalField(null=False, max_digits=12, decimal_places=2)
    product = fields.ForeignKeyField(
        "models.Product", related_name="measurement_units"
    )
