from datetime import datetime
import typing as t
import pydantic as pyd


class RefundTransactionIn(pyd.BaseModel):
    currency: str = "NGN"
    reference: str
    amount: pyd.condecimal(max_digits=12, decimal_places=2)
    reason: t.Optional[str]
    customer_note: t.Optional[str]
    merchant_note: t.Optional[str]


class IRefundTransaction(pyd.BaseModel):
    reference: str
    amount: int
    paid_at: str
    channel: str
    currency: str


class IRefundData(pyd.BaseModel):
    transaction: IRefundTransaction
    deducted_amount: int
    merchant_note: str
    customer_note: str
    amount: int
    is_deleted: bool
    fully_deducted: bool
    createdAt: str
    updatedAt: str


class IRefundSingleResponse(pyd.BaseModel):
    status: bool
    message: str
    data: t.Optional[IRefundData]


class IRefundListResponse(pyd.BaseModel):
    status: bool
    message: str
    data: t.List[t.Optional[IRefundData]]
