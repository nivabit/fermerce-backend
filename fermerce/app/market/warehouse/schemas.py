import typing as t
import uuid
import pydantic as pyd
from fermerce.core.schemas.response import IResponseFilterOut


class IWarehouseIn(pyd.BaseModel):
    street: str = pyd.Field(max_length=(100))
    city: str = pyd.Field(max_length=(100))
    phones: t.Optional[t.List[str]]
    state: uuid.UUID
    zipcode: str = pyd.Field(max_length=(10))


class IWarehouseOut(pyd.BaseModel):
    id: uuid.UUID
    phones: t.Optional[str]

    class Config:
        extra = "allow"
        orm_mode = True


class IIWarehouseListOut(IResponseFilterOut):
    results: t.Optional[t.List[IWarehouseOut]] = []

    class Config:
        orm_mode = True
