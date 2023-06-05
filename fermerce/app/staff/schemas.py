import re
import typing as t
import uuid
import pydantic as pyd
from fermerce.app.permission import schemas as perm_schema
from fermerce.core.schemas.response import IResponseFilterOut
from fermerce.app.user.utils import IUserOutFull


class IStaffIn(pyd.BaseModel):
    user_id: uuid.UUID

    class Config:
        schema_extra = {"example": {"user_id": uuid.uuid4()}}


class IStaffOut(pyd.BaseModel):
    id: uuid.UUID
    tel: t.Optional[str]
    permissions: t.List[perm_schema.IPermissionOut] = []

    class Config:
        orm_mode = True
        extra = "allow"
        schema_extra = {
            "example": {
                "firstname": "John",
                "aud": "st-vguytt",
                "lastname": "Doe",
                "email": "john@doe.com",
                "permissions": [
                    {
                        "name": "admin",
                    }
                ],
                "is_active": True,
                "is_suspected": True,
                "is_verified": True,
            }
        }


class IStaffOutFull(pyd.BaseModel):
    user: IUserOutFull

    class Config:
        orm_mode = True
        extra = "allow"
        schema_extra = {
            "example": {
                "firstname": "John",
                "lastname": "Doe",
                "email": "john@doe.com",
                "tel": "08089223577 or +234",
                "permissions": [
                    {
                        "name": "admin",
                    }
                ],
                "is_active": True,
                "is_suspected": True,
                "is_verified": True,
            }
        }


class IStaffOutList(IResponseFilterOut):
    results: t.List[t.Union[IStaffOut, IStaffOutFull]] = []


class IStaffRoleUpdate(pyd.BaseModel):
    staff_id: str
    permissions: t.List[uuid.UUID]


class IRemoveStaff(pyd.BaseModel):
    staff_id: str
    permanent: bool = False
