import typing as t
from datetime import datetime
import uuid
import pydantic as pyd


class IReviewIn(pyd.BaseModel):
    review_id: uuid.UUID
    comment: str = pyd.Field(None, max_length=250)
    rating: int = pyd.Field(..., ge=0, lt=11)
    product_id: int = None
    review_medias: t.List[uuid.UUID]


class IReviewUserOut(pyd.BaseModel):
    firstname: str
    lastname: str
    email: str


class IReviewProductOut(pyd.BaseModel):
    id: uuid.UUID
    name: str
    description: str
    slug: str


class IReviewOut(pyd.BaseModel):
    id: int
    comment: str
    rating: int
    order_id: str
    product: IReviewProductOut
    user: IReviewUserOut
    created_at: datetime
