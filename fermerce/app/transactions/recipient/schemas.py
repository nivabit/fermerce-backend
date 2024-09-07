import typing as t
import uuid
import pydantic as pyd


class IBankInBase(pyd.BaseModel):
    bvn: str


class IBankIn(IBankInBase):
    vendor_id: uuid.UUID
    bank_code: str
    account_number: str
    account_name: str
    type: str = "nuban"
    currency: str = "NGN"


class IBankUpdateIn(pyd.BaseModel):
    vendor_id: uuid.UUID
    bank_code: str
    account_number: str
    account_name: str
    type: str = "nuban"
    currency: str = "NGN"
