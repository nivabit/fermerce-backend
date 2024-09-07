from edgy import fields
from fermerce.core.model.base_model import BaseModel


class WereHouse(BaseModel):
    street = fields.CharField(max_length=100)
    city = fields.CharField(max_length=100)
    phones = fields.CharField(max_length=100, null=True)
    zipcode = fields.CharField(max_length=10, null=True)
    state = fields.ForeignKey(
        "State",
        related_name="warehouse",
        on_delete=fields.SET_NULL,
        null=True,
    )
    orders = fields.ManyToManyField(
        "Order",
        related_name="warehouse",
        through="fm__rel_order_warehouse",
    )
