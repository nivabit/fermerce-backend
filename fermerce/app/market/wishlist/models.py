from edgy import fields
from fermerce.core.model.base_model import BaseModel


class WishList(BaseModel):
    product = fields.ForeignKey("models.Product")
    quantity = fields.IntegerField(default=0, null=False)
    user = fields.ForeignKey("User", related_name="carts")
    selling_unit = fields.ForeignKey("ProductSellingUnit")
