from edgy import fields

from fermerce.core.model.base_model import BaseModel


class Cart(BaseModel):
    product = fields.ForeignKey("Product")
    quantity = fields.IntegerField(default=0, null=False)
    user = fields.ForeignKey("User", related_name="wishlist")
    selling_unit = fields.ForeignKey("ProductSellingUnit")
