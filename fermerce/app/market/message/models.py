from edgy import fields

from fermerce.core.model.base_model import BaseModel


class Message(BaseModel):
    vendor = fields.ForeignKey("Vendor", related_name="messages")
    sender = fields.ForeignKey("Staff", related_name="messages", null=True)
    message = fields.CharField(max_length=300)
    read = fields.BooleanField(default=False)
