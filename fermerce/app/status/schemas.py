import typing as t
import uuid
import pydantic as pyd

from fermerce.core.schemas.response import IResponseFilterOut


class IStatusIn(pyd.BaseModel):
    name: pyd.constr(max_length=30, min_length=4, strip_whitespace=True)


class IStatusOut(pyd.BaseModel):
    id: t.Optional[uuid.UUID]
    name: t.Optional[str]

    class Config:
        orm_mode = True


class IStatusOutList(IResponseFilterOut):
    results: t.List[IStatusOut] = []
