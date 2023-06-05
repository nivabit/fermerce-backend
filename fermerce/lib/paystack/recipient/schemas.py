import typing as t
import pydantic as pyd


class IMetaData(pyd.BaseModel):
    total: int
    skipped: int
    perPage: int
    page: int
    pageCount: int


class ITransactionRecipientIn(pyd.BaseModel):
    type: str = "nuban"
    name: str
    account_number: str
    bank_code: str
    currency: str = "NGN"

    class Config:
        extra = "allow"


class BankAccountDetails(pyd.BaseModel):
    account_number: str
    account_name: t.Optional[str]
    bank_code: str
    bank_name: str


# create transfer recipient bank full response response
class TransferRecipientData(pyd.BaseModel):
    active: bool
    currency: str
    name: str
    recipient_code: str
    type: str
    details: BankAccountDetails


# create transfer recipient response schema
class TransferRecipientResponse(pyd.BaseModel):
    status: bool
    message: str
    data: TransferRecipientData


class TransferRecipientListResponse(TransferRecipientResponse):
    status: bool
    message: str
    data: t.List[TransferRecipientData]
    meta: IMetaData


class TransferBulkRecipientData(pyd.BaseModel):
    success: t.List[TransferRecipientData]


class TransferRecipientBulkResponse(pyd.BaseModel):
    status: bool
    message: str
    data: TransferBulkRecipientData
    errors: t.List[t.Any]
