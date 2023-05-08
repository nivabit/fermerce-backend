import uuid
import datetime
import typing as t
import pydantic as pyd
from fermerce.app.markets.country.schemas import ICountryOut
from fermerce.app.markets.state.schemas import IStateOut
from fermerce.app.medias.schemas import IMediaOut
from fermerce.app.users.user.utils import IUserOutFull
from fermerce.core.schemas.response import IResponseFilterOut


class IVendorIn(pyd.BaseModel):
    business_name: str
    logo: t.Optional[str] = "example.png"
    states: t.List[uuid.UUID] = []
    countries: t.List[uuid.UUID] = []


class IRemoveVendor(pyd.BaseModel):
    vendor_id: str
    permanent: bool = False


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
