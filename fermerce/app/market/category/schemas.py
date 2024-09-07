import typing as t
import datetime
import uuid
import pydantic as pyd

from fermerce.core.schemas.response import IResponseFilterOut


class ProductCategoryIn(pyd.BaseModel):
    name: str = pyd.Field(max_length=30, min_length=4)

    class Config:
        json_schema_extra = {"example": {"name": "Tubber"}}


class ProductCategoryOut(pyd.BaseModel):
    id: t.Optional[uuid.UUID]
    name: t.Optional[str]
    created_at: t.Optional[datetime.datetime]
    updated_at: t.Optional[datetime.datetime]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "12345678-1234-1234-1234-123456789abc",
                "name": "Tubber",
                "created_at": "2022-10-25",
                "updated_at": "2022-10-25",
            }
        }
