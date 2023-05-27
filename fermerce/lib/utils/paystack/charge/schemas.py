import typing as t
import pydantic as pyd


class IChargeRequest(pyd.BaseModel):
    email: str
    amount: int
    reference: str


class IChargeRequestData(pyd.BaseModel):
    authorization_url: str
    access_code: str
    reference: str


class IChargeRequestOut(pyd.BaseModel):
    status: bool
    message: str
    data: t.Optional[IChargeRequestData]


class ISavedCardChargeIn(pyd.BaseModel):
    email: str
    amount: int
    authorization_code: str


class ILogHistory(pyd.BaseModel):
    type: str
    message: str
    time: int


class ILog(pyd.BaseModel):
    start_time: int
    time_spent: int
    attempts: int
    errors: int
    success: bool
    mobile: bool
    input: t.List[str]
    history: t.List[ILogHistory]


class IAuthorization(pyd.BaseModel):
    authorization_code: str
    bin: str
    exp_year: str
    card_type: str
    bank: str
    country_code: str
    brand: str
    reusable: bool
    account_name: t.Optional[str]


class Data(pyd.BaseModel):
    id: int
    reference: str
    amount: int
    channel: str
    currency: str
    ip_address: str
    fees: int
    log: ILog
    authorization: IAuthorization


class IChargeResponse(pyd.BaseModel):
    status: bool
    message: str
    data: t.Optional[Data]
