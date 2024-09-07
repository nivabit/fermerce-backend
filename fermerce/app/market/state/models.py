from edgy import fields
from fermerce.core.model.base_model import BaseModel


class State(BaseModel):
    """
    The Available state
    """

    name = fields.CharField(max_length=50, null=True)
