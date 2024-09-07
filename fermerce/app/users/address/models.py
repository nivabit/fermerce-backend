from uuid_extensions import uuid7str
from edgy import fields
from fermerce.core.model.base_model import BaseModel


class Address(BaseModel):
    street = fields.CharField(max_length=100)
    city = fields.CharField(max_length=100)
    phones = fields.CharField(max_length=100, null=True)
    state = fields.ForeignKey("State", related_name="address")
    zipcode = fields.CharField(max_length=10, null=True)
