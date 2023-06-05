import typing as t
import pydantic as pyd


class RefundTransactionIn(pyd.BaseModel):
    currency: str = "NGN"
    reference: str
    amount: pyd.condecimal(max_digits=12, decimal_places=2)
    customer_note: str
    merchant_note: t.Optional[str]


class IRefundData(pyd.BaseModel):
    deducted_amount: int
    merchant_note: str
    customer_note: str
    amount: int
    is_deleted: bool
    fully_deducted: bool
