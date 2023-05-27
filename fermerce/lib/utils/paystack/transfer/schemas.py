from datetime import datetime
import typing as t
import pydantic as pyd


class IMetaData(pyd.BaseModel):
    total: int
    skipped: int
    perPage: int
    page: int
    pageCount: int


class ITransferValidatedIn(pyd.pyd.BaseModel):
    otp: str
    transfer_code: str


class TransferData(pyd.BaseModel):
    amount: int
    reference: t.Optional[str]
    reason: str
    recipient: str


class TransferDataSingleResponse(TransferData):
    status: str
    transfer_code: str


class ITransferDataIn(TransferData):
    source: str = "balance"
    reason: t.Optional[str] = "initiated by admin"


class ICreateTransferResponse(pyd.BaseModel):
    status: bool
    message: t.Optional[str]
    data: t.Optional[TransferDataSingleResponse]


class ICreateTransferListResponse(pyd.BaseModel):
    status: bool
    message: t.Optional[str]
    transfers: t.List[TransferData]


class ITransferListResponse(pyd.BaseModel):
    status: bool
    message: t.Optional[str]
    data: t.List[TransferData] = []
    meta: IMetaData


# transfer recipient
class ITransferRecipientDetails(pyd.BaseModel):
    account_number: str
    account_name: t.Optional[str]
    bank_code: str
    bank_name: str


class ITransferRecipientData(pyd.BaseModel):
    domain: str
    type: str
    currency: str
    name: str
    details: ITransferRecipientDetails
    description: t.Optional[str]
    metadata: t.Optional[dict]
    recipient_code: str
    active: bool
    id: int
    integration: int
    createdAt: datetime
    updatedAt: datetime


class TransferData(pyd.BaseModel):
    integration: int
    recipient: ITransferRecipientData
    domain: str
    amount: int
    currency: str
    source: str
    source_details: t.Optional[dict]
    reason: str
    status: str
    failures: t.Optional[dict]
    transfer_code: str
    id: int
    createdAt: datetime
    updatedAt: datetime


class TransferListData(pyd.BaseModel):
    data: t.List[TransferData]


class ITransferListResponse(pyd.BaseModel):
    status: bool
    message: str
    data: TransferListData
    meta: IMetaData
