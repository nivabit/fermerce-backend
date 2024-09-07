from edgy import fields

from fermerce.core.model.base_model import BaseModel


class Country(BaseModel):
    """
    The Available country
    """

    name = fields.CharField(max_length=50, null=True)
