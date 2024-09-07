import typing as t
import uuid
import pydantic as pyd


class IMediaIn(pyd.BaseModel):
    url: pyd.AnyUrl


class IMediaOut(pyd.BaseModel):
    id: uuid.UUID
    url: pyd.AnyUrl
    content_type: t.Optional[str]
    alt: t.Optional[str]

    class Config:
        orm_mode = True


class IMediaDeleteIn(pyd.BaseModel):
    uris: t.List[str] = []
    trash = False
