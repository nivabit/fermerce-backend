import typing as t
import datetime
import uuid
import pydantic as pyd

from fermerce.core.schemas.response import IResponseFilterOut


class IMeasuringUnitIn(pyd.BaseModel):
    unit: pyd.constr(max_length=30, min_length=2, strip_whitespace=True)

    class Config:
        schema_extra = {"example": {"unit": "kg"}}


class IMeasuringUnitOut(pyd.BaseModel):
    id: t.Optional[uuid.UUID]
    unit: t.Optional[str]
    created_at: t.Optional[datetime.datetime]
    updated_at: t.Optional[datetime.datetime]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "12345678-1234-1234-1234-123456789abc",
                "unit": "edit_product",
                "created_at": "2022-10-25",
                "updated_at": "2022-10-25",
            }
        }


class IProductMeasuringUnitBase(pyd.BaseModel):
    unit_id: uuid.UUID
    size: int
    price: pyd.condecimal(max_digits=12, decimal_places=2)


class IProductMeasuringUnitIn(IProductMeasuringUnitBase):
    product_id: uuid.UUID
    selling_units: t.List[IProductMeasuringUnitBase]


class IProductMeasuringUnitOut(pyd.BaseModel):
    id: uuid.UUID
    size: int
    price: pyd.condecimal(max_digits=12, decimal_places=2)


class IProductRemoveMeasuringUnitIn(pyd.BaseModel):
    product_id: uuid.UUID
    unit_id: uuid.UUID


class IMeasuringUnitOutList(IResponseFilterOut):
    results: t.List[IMeasuringUnitOut] = []
