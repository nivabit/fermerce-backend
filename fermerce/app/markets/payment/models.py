from tortoise import fields, models

from fermerce.lib.utils.random_string import generate_orderId


class Payment(models.Model):
    reference = fields.CharField(max_length=16, default=lambda: generate_orderId(15))
    total = fields.DecimalField(decimal_places=2, max_digits=12)
    discount_given = fields.FloatField(default=0.0)
    user = fields.ForeignKeyField("models.User", related_name="payments")
    status = fields.ForeignKeyField("models.Status")
    order = fields.ForeignKeyField("models.Order", related_name="payment")
