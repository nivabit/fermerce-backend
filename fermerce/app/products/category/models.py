import uuid
from tortoise import fields, models


class ProductCategory(models.Model):
    """
    The Available categories
    """

    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=50, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
