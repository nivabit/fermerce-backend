import typing as t
import datetime
import uuid
import pydantic as pyd

from fermerce.core.schemas.response import IResponseFilterOut


class IDeliveryModeIn(pyd.BaseModel):
    name: pyd.constr(max_length=30, min_length=4, strip_whitespace=True)
    price: pyd.condecimal(max_digits=12, decimal_places=2)

    class Config:
        schema_extra = {"example": {"name": "express", "price": 10000}}


class IDeliveryModeOut(pyd.BaseModel):
    id: t.Optional[uuid.UUID]
    name: str
    price: pyd.condecimal(max_digits=12, decimal_places=2)
    created_at: t.Optional[datetime.datetime]
    updated_at: t.Optional[datetime.datetime]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "12345678-1234-1234-1234-123456789abc",
                "name": "express",
                "created_at": "2022-10-25",
                "updated_at": "2022-10-25",
            }
        }


class IDeliveryModeList(IResponseFilterOut):
    results: t.List[IDeliveryModeOut] = []
