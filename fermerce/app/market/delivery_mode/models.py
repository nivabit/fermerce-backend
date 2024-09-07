from edgy import fields
from fermerce.core.model.base_model import BaseModel


class DeliveryMode(BaseModel):
    price = fields.DecimalField(max_digits=12, decimal_places=2)
    name = fields.CharField(max_length=50, null=True)

    class Meta:
        tablename = "fm_order_delivery_mode"
