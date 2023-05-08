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
    discount: t.Optional[float]
    single: bool = True
    start: t.Optional[datetime.date] = datetime.datetime.today()
    end: t.Optional[datetime.date] = datetime.datetime.today() + datetime.timedelta(
        days=7
    )


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


class IProductPromoCodeOut(IProductPromoCodeIn):
    id: t.Optional[uuid.UUID]
    pass

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "12345678-1234-1234-1234-123456789abc",
                "code": "12343439klf3",
                "discount": 10.0,
                "start": "12345678-1234-1234",
                "end": "12345678-1234-1234",
                "created_at": "2022-10-25",
                "updated_at": "2022-10-25",
            }
        }


class IProductPromoCodeListOut(IResponseFilterOut):
    results: t.Optional[t.List[IProductPromoCodeOut]] = []
