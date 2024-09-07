from edgy import fields
from fermerce.core.model.base_model import BaseModel


class ProductDetail(BaseModel):
    title = fields.CharField(max_length=50, null=False)
    description = fields.TextField(null=False)
    product = fields.ForeignKey("models.Product", related_name="details")
 