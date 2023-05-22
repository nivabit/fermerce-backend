import typing as t
import pydantic as pyd
import uuid


class IPaymentCardIn(pyd.BaseModel):
    order_id: uuid.UUID
    cardno: pyd.PaymentCardNumber
    cvv: str = pyd.Field(
        ..., title="card cvv", description="Customer cvv", max_length=3, min_length=3
    )
    expirymonth: str = pyd.Field(
        ..., title="card expire month", description="Customer card expire month"
    )
    expiryyear: str = pyd.Field(
        ..., title="card expire year", description="Customer card expire year"
    )
    phonenumber: t.Optional[str]
    pin: str = pyd.Field(
        ...,
        title="card pin",
        description="Customer card pin",
        min_length=4,
        max_length=4,
    )
    suggested_auth: str = pyd.Field(
        title="card authentication mode",
        description="what mode is Customer card supported e.g PIN, Address but for now we support pin only",
        default="pin",
    )


class IPaymentVerificationResponse(pyd.BaseModel):
    flwRef: t.Optional[str]
    cardToken: t.Optional[str]
    chargedAmount: t.Optional[int]
    amount: t.Optional[int]
    transactionComplete: t.Optional[bool] = False
    error: t.Optional[bool] = False
    txRef: t.Optional[str]


class ICardChargeOut(pyd.BaseModel):
    order_id: uuid.UUID
    message: str


class ICardChargeResponse(pyd.BaseModel):
    validationRequired: t.Optional[bool] = False
    suggestedAuth: t.Optional[str] = "PIN"
    flwRef: str
    authUrl: t.Optional[str]
    error: t.Optional[bool] = False
    txRef: str


class IValidationOut(pyd.BaseModel):
    messages: str
    order_id: uuid.UUID


class IPaymentValidationResponse(pyd.BaseModel):
    error: bool
    txRef: str
    flwRef: str
    errMsg: str = None


class IPaymentUserIn(pyd.BaseModel):
    email: str
    phonenumber: str
    firstname: str
    lastname: str
    IP: t.Optional[pyd.IPvAnyAddress]
    txRef: str
    amount: float


class IValidatedPaymentIn(pyd.BaseModel):
    otp: str
    order_id: uuid.UUID


class TransactionData(pyd.BaseModel):
    settlement_id: str = pyd.Field(alias="settlementId")
    id: int
    AccountId: int
    TransactionId: int
    FlwRef: str
    walletId: int
    AmountRefunded: str
    status: str
    destination: str
    meta: str
    updatedAt: str
    createdAt: str


class IRefundDataIn(pyd.BaseModel):
    order_id: uuid.UUID
    amount: float


class IRefundResponse(pyd.BaseModel):
    status: bool
    data: TransactionData


def convert_to_pydantic(data: t.Tuple[bool, dict]) -> IRefundResponse:
    status, inner_data = data
    return IRefundResponse(status=status, data=TransactionData(**inner_data))
