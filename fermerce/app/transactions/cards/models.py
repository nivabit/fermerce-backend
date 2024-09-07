from edgy import fields

from fermerce.core.model.base_model import BaseModel


class SaveCard(BaseModel):
    user = fields.ForeignKey("User", related_name="payment_cards")
    authorization_code = fields.CharField(max_length=100, null=False)
    bin = fields.CharField(max_length=8, null=False)
    last4 = fields.CharField(max_length=8, null=True)
    exp_month = fields.CharField(max_length=4, null=True)
    exp_year = fields.CharField(max_length=4)
    card_type = fields.CharField(max_length=20)
    bank = fields.CharField(max_length=100)
    country_code = fields.CharField(max_length=20)
    brand = fields.CharField(max_length=20)
    reusable = fields.BooleanField(default=False)
