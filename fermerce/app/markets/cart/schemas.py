import typing as t
import uuid
import pydantic as pyd
from fermerce.app.products.product import schemas as product_schema


class ICartIn(pyd.BaseModel):
    quantity: int = pyd.Field(default=1, gt=0)
    selling_unit: uuid.UUID
    product_id: uuid.UUID


class ICartOut(pyd.BaseModel):
    id: uuid.UUID
    quantity: int = 1
    product: product_schema.IProductLongInfo

    class Config:
        orm_mode = True
