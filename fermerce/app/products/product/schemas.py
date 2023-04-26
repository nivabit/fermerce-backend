import typing as t
import uuid
import pydantic as pyd
from fermerce.app.medias import schemas as media_schema
from fermerce.app.products.category import schemas as category_schema
from fermerce.app.medias import schemas as media_schema


class IProductDetailBase(pyd.BaseModel):
    detail_id: uuid.UUID
    product_id: uuid.UUID


class IProductDetails(pyd.BaseModel):
    title: str
    description: str


class IProductDetailsIn(IProductDetailBase):
    product_id: uuid.UUID
    details: t.List[IProductDetails]


class IProductDetailsRemoveIn(IProductDetailBase):
    detail_id: uuid.UUID
    product_id: uuid.UUID


class IProductDetailsOut(IProductDetails):
    id: uuid.UUID


class IProductIn(pyd.BaseModel):
    name: str
    description: str
    in_stock: bool = True
    galleries: t.List[str] = []
    cover_img: t.Optional[str]
    categories: t.List[t.Optional[uuid.UUID]] = []


class IProductShortInfo(pyd.BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str
    sku: str
    in_stock: bool
    galleries: t.List[media_schema.IMediaOut] = []
    cover_media: t.Optional[media_schema.IMediaOut]

    class Config:
        orm_mode = True


class IProductLongInfo(IProductShortInfo):
    id: uuid.UUID
    categories: t.List[category_schema.IProductCategoryOut]
    details: t.List[IProductDetailsIn] = []

    class Config:
        orm_mode = True
