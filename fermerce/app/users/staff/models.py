import uuid
from tortoise import fields, models
from fermerce.lib.utils.random_string import random_str


class Staff(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    staff_id = fields.CharField(
        max_length=10,
        default=f"st-{random_str(5)}",
    )
    user = fields.OneToOneField(
        "models.User", on_delete=fields.CASCADE, related_name="staff"
    )
    permissions = fields.ManyToManyField(
        "models.Permission",
        related_name="staffs",
        through="staff_permissions",
    )
    tel = fields.CharField(max_length=17, null=True)
    is_suspended = fields.BooleanField(default=False, null=True)
    is_active = fields.BooleanField(default=True, null=True)
    is_archived = fields.BooleanField(default=False, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
