import pydantic as pyd
import typing as t
import uuid


class IUserOutFull(pyd.BaseModel):
    id: t.Optional[uuid.UUID]
    email: t.Optional[pyd.EmailStr]
    username: t.Optional[str]
    lastname: t.Optional[str]
    firstname: t.Optional[str]
    is_active: t.Optional[bool] = False
    is_suspended: t.Optional[bool] = False
    is_verified: t.Optional[bool] = False

    class Config:
        extra = "allow"
        fields = {"password": {"exclude": True}}
