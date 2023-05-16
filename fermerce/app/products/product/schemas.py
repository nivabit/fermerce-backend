import typing as t
import uuid
import pydantic as pyd

from fermerce.core.schemas.response import IResponseFilterOut


class IProductIn(pyd.BaseModel):
    name: str
    description: str
    in_stock: bool = True
    galleries: t.List[str] = []
    cover_img: t.Optional[uuid.UUID]
    categories: t.List[t.Optional[uuid.UUID]] = []


class IProductOut(pyd.BaseModel):
    id: t.Optional[uuid.UUID]

    class Config:
        extra = "allow"
        orm_mode = True


class IProductListOut(IResponseFilterOut):
    results: t.Optional[t.List[IProductOut]]

    class Config:
        extra = "allow"
        orm_mode = True
