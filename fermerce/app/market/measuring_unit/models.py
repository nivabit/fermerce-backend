from edgy import fields
from fermerce.core.model.base_model import BaseModel


class MeasuringUnit(BaseModel):
    """
    The Available state
    """

    unit = fields.CharField(max_length=50, null=True)
