import typing as t
import datetime
import uuid
import pydantic as pyd
from fermerce.core.schemas.response import IResponseFilterOut

from fermerce.lib.utils.random_string import random_str


class IProductPromoCodeBase(pyd.BaseModel):
    code: pyd.constr(max_length=10, min_length=4, strip_whitespace=True) = random_str(
        10
    )
    discount: t.Optional[float] = 0.1
    single: bool = True
    start: t.Optional[datetime.date] = datetime.datetime.utcnow().date()
    end: t.Optional[
        datetime.date
    ] = datetime.datetime.utcnow().date() + datetime.timedelta(days=7)


class IProductPromoCodeIn(IProductPromoCodeBase):
    pass


class IProductPromoCodeUpdateIn(pyd.BaseModel):
    promo_code_id: uuid.UUID
    products: t.List[uuid.UUID]


class IProductPromoCodeRemoveIn(pyd.BaseModel):
    promo_code_id: uuid.UUID
    products: t.List[uuid.UUID]

    # class Config:
    #     schema_extra = {"example": {"code": "12343439klf3", }}


class IProductPromoCodeOut(pyd.BaseModel):
    id: t.Optional[uuid.UUID]
    code: t.Optional[str]
    discount: t.Optional[float]
    single: t.Optional[bool]
    active_from: t.Optional[datetime.date]
    active_to: t.Optional[datetime.date]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "12345678-1234-1234-1234-123456789abc",
                "code": "12343439klf3",
                "discount": 0.3,
                "start": "2022-10-25",
                "end": "2022-10-30",
                "created_at": "2022-10-25",
                "updated_at": "2022-10-25",
            }
        }


class IProductPromoCodeListOut(IResponseFilterOut):
    results: t.Optional[t.List[IProductPromoCodeOut]] = []
