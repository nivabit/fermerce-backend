import typing as t
import uuid
import pydantic as pyd

from fermerce.core.schemas.response import IResponseFilterOut


class IStateIn(pyd.BaseModel):
    name: pyd.constr(max_length=30, min_length=3, strip_whitespace=True)


class IStateOut(pyd.BaseModel):
    id: t.Optional[uuid.UUID]
    name: t.Optional[str]

    class Config:
        orm_mode = True


class IStateOutList(IResponseFilterOut):
    results: t.List[IStateOut] = []
