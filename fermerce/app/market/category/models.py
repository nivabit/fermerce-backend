from edgy import fields
from fermerce.core.model.base_model import BaseModel


class ProductCategory(BaseModel):
    """
    The Available product categories
    """

    name = fields.CharField(max_length=50, null=True)
