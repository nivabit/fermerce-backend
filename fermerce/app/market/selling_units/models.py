from edgy import fields

from fermerce.core.model.base_model import BaseModel


class ProductSellingUnit(BaseModel):
    unit = fields.ForeignKey("MeasuringUnit", related_name=None)
    size = fields.IntegerField(null=False, default=5)
    price = fields.DecimalField(null=False, max_digits=12, decimal_places=2)
    product = fields.ForeignKey("Product", related_name="measurement_units")
