import typing as t
import uuid
import pydantic as pyd


class IProductDetailBase(pyd.BaseModel):
    detail_id: uuid.UUID
    product_id: uuid.UUID


class IProductDetails(pyd.BaseModel):
    title: str
    description: str


class IProductDetailsIn(pyd.BaseModel):
    product_id: uuid.UUID
    details: t.List[IProductDetails]


class IProductDetailsRemoveIn(pyd.BaseModel):
    detail_ids: t.List[uuid.UUID]
    product_id: uuid.UUID


class IProductDetailsUpdateIn(IProductDetails):
    detail_id: uuid.UUID
    product_id: uuid.UUID


class IProductDetailsOut(IProductDetails):
    id: uuid.UUID
