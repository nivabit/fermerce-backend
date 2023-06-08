import uuid
from tortoise import fields, models


class WereHouse(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    street = fields.CharField(max_length=100)
    city = fields.CharField(max_length=100)
    phones = fields.CharField(max_length=100, null=True)
    zipcode = fields.CharField(max_length=10, null=True)
    state = fields.ForeignKeyField(
        "models.State",
        related_name="warehouse",
        on_delete=fields.SET_NULL,
        null=True,
    )
    orders = fields.ManyToManyField(
        "models.Order",
        related_name="warehouse",
        through="fm__rel_order_warehouse",
    )
    created = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "fm_warehouse_review"
