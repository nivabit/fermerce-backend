import datetime
import uuid
import pydantic as pyd


class IMessageIn(pyd.BaseModel):
    message: str
    vendor_id: uuid.UUID


class IMessageOut(IMessageIn):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        extra = "allow"
