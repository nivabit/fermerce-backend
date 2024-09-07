import uuid
import datetime
import typing as t
import pydantic as pyd
from fermerce.app.medias.schemas import IMediaOut
from fermerce.lib.paystack.verification.schemas import IBankAccountValidateIn
from fermerce.app.user.utils import IUserOutFull
from fermerce.core.schemas.response import IResponseFilterOut


class IVendorBase(pyd.BaseModel):
    business_name: str
    logo: t.Optional[uuid.UUID]
    phone_number: str
    email: pyd.EmailStr


class IVendorIn(IVendorBase):
    password: pyd.SecretStr


class IVendorUpdateIn(IVendorBase):
    password: pyd.SecretStr


class IRemoveVendor(pyd.BaseModel):
    vendor_id: str
    permanent: bool = False


class IGetPasswordResetLink(pyd.BaseModel):
    email: pyd.EmailStr


class IUserResetPassword(pyd.BaseModel):
    token: str
    password: pyd.SecretStr


class ICheckUserEmail(pyd.BaseModel):
    username: t.Optional[str]


class IUserResetPasswordNoToken(pyd.BaseModel):
    password: pyd.SecretStr
    old_password: pyd.SecretStr


class IUserAccountVerifyToken(pyd.BaseModel):
    token: str


class IUserResetForgetPassword(pyd.BaseModel):
    email: pyd.EmailStr


class IVendorOutFull(pyd.BaseModel):
    user: t.Optional[IUserOutFull]

    class Config:
        orm_mode = True
        extra = "allow"


class IVendorListOut(IResponseFilterOut):
    results: t.List[IVendorOutFull] = []


class IVendorOut(pyd.BaseModel):
    id: uuid.UUID
    business_name: str
    logo: t.Optional[IMediaOut]
    user: IUserOutFull
    is_active: bool = False
    rating: float = 0.0
    created_at: t.Optional[datetime.datetime] = datetime.datetime.now()
    modified_at: t.Optional[datetime.datetime] = None

    class Config:
        orm_mode = True


#  verification of vendor account and information


class IVendorOwner(pyd.BaseModel):
    firstname: str = pyd.Field(max_length=40)
    lastname: str = pyd.Field(max_length=40)
    email: str = pyd.Field(max_length=40)
    identification_number: str
    phone: str
    manager_dob: datetime.date


class IBankAccountVerificationIn(IBankAccountValidateIn):
    pass


class IVendorVerificationIn(pyd.BaseModel):
    bank: t.Optional[IBankAccountValidateIn]
    owner: t.Optional[IVendorOwner]
