import uuid
import datetime
import typing as t
import pydantic as pyd
from fermerce.app.markets.country.schemas import ICountryOut
from fermerce.app.markets.state.schemas import IStateOut
from fermerce.app.medias.schemas import IMediaOut
from fermerce.app.users.user.schemas import IUserOut


class IVendorIn(pyd.BaseModel):
    business_name: str
    logo: t.Optional[str] = "example.png"
    states: t.List[uuid.UUID] = []
    countries: t.List[uuid.UUID] = []


class IRemoveVendor(pyd.BaseModel):
    vendor_id: str
    permanent: bool = False


class IVendorOutFull(pyd.BaseModel):
    id: uuid.UUID
    business_name: str
    rating: float = 0.0
    is_active: bool = False
    logo: t.Optional[IMediaOut]
    countries: t.Optional[t.List[ICountryOut]]
    states: t.Optional[t.List[IStateOut]] = []
    user: IUserOut
    created_at: t.Optional[datetime.datetime] = datetime.datetime.now()
    modified_at: t.Optional[datetime.datetime] = None

    class Config:
        orm_mode = True


class IVendorOut(pyd.BaseModel):
    id: uuid.UUID
    business_name: str
    logo: t.Optional[IMediaOut]
    user: IUserOut
    is_active: bool = False
    rating: float = 0.0
    created_at: t.Optional[datetime.datetime] = datetime.datetime.now()
    modified_at: t.Optional[datetime.datetime] = None

    class Config:
        orm_mode = True
