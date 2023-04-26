import datetime
import typing as t
import uuid
import pydantic as pyd


class ITrackIn(pyd.BaseModel):
    order_item_tracking_id: str = pyd.Field(..., description="tracking ID")
    location: str = pyd.Field(..., description="Location")
    note: t.Optional[str]


class ITrackOut(ITrackIn):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
