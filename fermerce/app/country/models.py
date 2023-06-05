import uuid
from tortoise import fields, models


class Country(models.Model):
    """
    The Available country
    """

    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=50, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "fm_country"
