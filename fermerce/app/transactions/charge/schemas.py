import typing as t
import pydantic as pyd
import uuid


class ICreateOrderPaymentIn(pyd.BaseModel):
    order_id: uuid.UUID


class IPaymentVerificationIn(pyd.BaseModel):
    reference: str
    save_card: bool = True


class CurrencyData(pyd.BaseModel):
    currency: str
    amount: int


class TransactionTotalsData(pyd.BaseModel):
    total_transactions: int
    unique_customers: int
    total_volume: int
    total_volume_by_currency: t.List[CurrencyData]
    pending_transfers: int
    pending_transfers_by_currency: t.List[CurrencyData]


class TransactionTotalsResponse(pyd.BaseModel):
    status: bool
    message: str
    data: TransactionTotalsData
