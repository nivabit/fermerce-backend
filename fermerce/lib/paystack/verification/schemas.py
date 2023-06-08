import typing as t
import pydantic as pyd


class IAccountResolveIn(pyd.BaseModel):
    account_number: str
    bank_code: str

    class Config:
        orm_mode = True


class IAccountResolveData(pyd.BaseModel):
    account_number: str
    account_name: str


class IAccountResolveResponse(pyd.BaseModel):
    status: bool
    message: str
    data: IAccountResolveData


class IBankAccountValidateIn(pyd.BaseModel):
    bank_code: str
    country_code: str = "NG"
    account_number: str
    account_name: str
    account_type: str
    document_type: str
    document_number: str

    class Config:
        orm_mode = True


class IAccountVerificationData(pyd.BaseModel):
    verified: t.Optional[bool]
    verificationMessage: t.Optional[str]


class IAccountVerificationResponse(pyd.BaseModel):
    status: bool
    message: str
    data: t.Optional[IAccountVerificationData]
