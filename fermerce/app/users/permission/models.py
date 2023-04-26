import uuid
from tortoise import fields, models

from fermerce.app.users.staff.models import Staff


class Permission(models.Model):
    """
    The Available
    """

    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=50, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    staffs: fields.ReverseRelation[Staff]

    def __str__(self):
        return self.name
