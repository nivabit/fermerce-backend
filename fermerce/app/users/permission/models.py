from edgy import fields
from fermerce.core.model.base_model import BaseModel


class Permission(BaseModel):
    """
    The Available
    """

    name = fields.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name
