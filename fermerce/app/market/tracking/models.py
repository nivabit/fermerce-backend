from edgy import fields
from fermerce.core.model.base_model import BaseModel


class Tracking(BaseModel):
    order_item = fields.ForeignKey("OrderItem", related_name="trackings")
    location = fields.CharField(max_length=300, null=True, blank=True)
    note = fields.TextField(null=True)
