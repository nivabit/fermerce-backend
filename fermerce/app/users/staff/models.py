from edgy import fields
from fermerce.core.model.base_model import BaseModel
from fermerce.lib.utils.random_string import random_str


class Staff(BaseModel):
    staff_id = fields.CharField(
        max_length=10,
        default=f"st-{random_str(5)}",
    )
    user = fields.OneToOneField(
        "models.User",
        on_delete=fields.CASCADE,
        related_name="staff",
    )
    permissions = fields.ManyToManyField(
        "Permission",
        related_name="staffs",
        through="fm_staff_permission",
    )
    tel = fields.CharField(max_length=17, null=True)
    is_suspended = fields.BooleanField(default=False, null=True)
    is_active = fields.BooleanField(default=True, null=True)
    is_archived = fields.BooleanField(default=False, null=True)
