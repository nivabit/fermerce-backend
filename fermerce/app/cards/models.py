import uuid
from tortoise import fields, models


class SaveCard(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="payment_cards")
    authorization_code = fields.CharField(max_length=100, null=False)
    bin = fields.CharField(max_length=8, null=False)
    last4 = fields.CharField(max_length=8, null=False)
    exp_month = fields.CharField(max_length=4)
    exp_year = fields.CharField(max_length=4)
    card_type = fields.CharField(max_length=20)
    bank = fields.CharField(max_length=100)
    country_code = fields.CharField(max_length=20)
    brand = fields.CharField(max_length=20)
    reusable = fields.BooleanField(default=False)
    created = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "fm_save_payment_card"
