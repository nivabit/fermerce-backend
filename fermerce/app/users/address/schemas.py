import typing as t
import uuid
import pydantic as pyd
from fermerce.app.markets.state.schemas import IStateIn
from fermerce.core.schemas.response import IResponseFilterOut


class IAddressIn(pyd.BaseModel):
    street: str = pyd.Field(max_length=(100))
    city: str = pyd.Field(max_length=(100))
    phones: t.Optional[t.List[str]]
    state: str = pyd.Field(max_length=(100))
    zipcode: str = pyd.Field(max_length=(10))


class IAddressOut(IAddressIn):
    id: uuid.UUID
    state: IStateIn

    class Config:
        orm_mode = True


class IAddressListOut(IResponseFilterOut):
    results: t.Optional[IAddressOut] = []

    class Config:
        orm_mode = True
