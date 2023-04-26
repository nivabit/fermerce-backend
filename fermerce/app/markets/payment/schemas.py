import datetime
import typing as t
import uuid
import pydantic as pyd

from fermerce.app.users.user import schemas as user_schema

from fermerce.app.markets.payment import enum
from fermerce.core.enum.frequent_duration import Frequent


class IPaymentOrderOut(pyd.BaseModel):
    id: uuid.UUID
    reference: str
    completed: bool
    total_payed: float


class IPaymentRevenueInDateRange(pyd.BaseModel):
    start_date: datetime.date
    end_date: datetime.date
    freq: Frequent = Frequent.daily


class IPaymentTrend(pyd.BaseModel):
    daily: float
    weekly: float
    monthly: float
    yearly: float


class IVerifyPaymentResponse(pyd.BaseModel):
    reference: str


class IPaymentIn(pyd.BaseModel):
    order_id: str


class ICustomer(pyd.BaseModel):
    order_id: str
    user_id: int
    email: pyd.EmailStr
    name: str


class IPaymentInitOut(pyd.BaseModel):
    paymentLink: str
    total_amount: pyd.condecimal(max_digits=10, decimal_places=2)


class PaymentMeta(pyd.BaseModel):
    user_id: int
    order_id: str


class IOrderInfo(pyd.BaseModel):
    id: uuid.UUID
    order_id: str
    user: user_schema.IUserOut
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class IPayment(pyd.BaseModel):
    id: uuid.UUID
    reference: str
    completed: bool
    order_id: str
    total_payed: float


class IPaymentVerifyOut(pyd.BaseModel):
    error: bool
    txRef: str
    amount: int
    transactionComplete: bool


class IDataIn(pyd.BaseModel):
    link: str


class IPaymentResponse(pyd.BaseModel):
    status: str
    message: str
    data: t.Optional[IDataIn]


class IPaymentLinkData(pyd.BaseModel):
    public_key: str
    amount: int
    tx_ref: str
    currency: enum.PaymentCurrency = enum.PaymentCurrency.NGN
    redirect_url: str = "https://webhook.site/9d0b00ba-9a69-44fa-a43d-a82c33c36fdc"
    user: ICustomer
    meta: PaymentMeta
