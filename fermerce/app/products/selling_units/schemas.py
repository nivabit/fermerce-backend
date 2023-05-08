import uuid
import pydantic as pyd
import typing as t


class IProductSellingUnitBase(pyd.BaseModel):
    size: int
    price: pyd.condecimal(max_digits=12, decimal_places=2)


class IProductSellingUnitIn(IProductSellingUnitBase):
    unit_id: uuid.UUID
    product_id: uuid.UUID


class IProductSellingUnitOut(pyd.BaseModel):
    id: uuid.UUID
    size: int
    price: pyd.condecimal(max_digits=12, decimal_places=2)


class IProductRemoveSellingUnitIn(pyd.BaseModel):
    product_id: uuid.UUID
    selling_unit_ids: t.List[uuid.UUID]
