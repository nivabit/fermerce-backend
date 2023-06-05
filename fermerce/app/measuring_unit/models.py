import uuid
from tortoise import fields, models


class MeasuringUnit(models.Model):
    """
    The Available state
    """

    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    unit = fields.CharField(max_length=50, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "fm_product_measuring_unit"
