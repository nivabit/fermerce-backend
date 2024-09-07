from edgy import fields
from fermerce.core.model.base_model import BaseModel
from fermerce.lib.utils.random_string import generate_orderId


class Charge(BaseModel):
    reference = fields.CharField(max_length=20, default=lambda: generate_orderId(15))
    total = fields.DecimalField(decimal_places=2, max_digits=12)
    user = fields.ForeignKey("User", related_name="payments")
    status = fields.ForeignKey("Status")
    order = fields.OneToOneField("Order", related_name="payment")

    @staticmethod
    def generate_order_reference():
        return generate_orderId(15)
