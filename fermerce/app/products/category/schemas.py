import typing as t
import datetime
import uuid
import pydantic as pyd

from fermerce.core.schemas.response import IResponseFilterOut


class IProductCategoryIn(pyd.BaseModel):
    name: pyd.constr(max_length=30, min_length=4, strip_whitespace=True)

    class Config:
        schema_extra = {"example": {"name": "Tubber"}}


class IProductCategoryOut(pyd.BaseModel):
    id: t.Optional[uuid.UUID]
    name: t.Optional[str]
    created_at: t.Optional[datetime.datetime]
    updated_at: t.Optional[datetime.datetime]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "12345678-1234-1234-1234-123456789abc",
                "name": "Tubber",
                "created_at": "2022-10-25",
                "updated_at": "2022-10-25",
            }
        }


class IProductCategoryOutList(IResponseFilterOut):
    results: t.List[IProductCategoryOut] = []
