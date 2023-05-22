import typing as t
from fermerce.app.markets.order.models import OrderItem
from fermerce.app.markets.payment import schemas
from fermerce.core.settings import config
from pydantic import condecimal, BaseModel
from fermerce.app.products.promo_code.models import ProductPromoCode
from rave_python.rave import Rave
from rave_python import rave_exceptions
from fermerce.lib.errors import error

rave = Rave(
    secretKey=config.payment_secret_key,
    publicKey=config.payment_public_key,
    production=config.debug,
    usingEnv=False,
)


def charge_card(data_in: schemas.IPaymentCardIn, user_detail: schemas.IPaymentUserIn):
    try:
        response = rave.Card.charge(
            {**data_in.dict(exclude={"order_id"}), **user_detail.dict()}
        )
        data_out = schemas.ICardChargeResponse(**response)
        if data_out.error:
            raise error.BadDataError(
                "Error charging card please check the card details and try again"
            )
        return data_out
    except rave_exceptions.CardChargeError as e:
        raise error.BadDataError(detail=e.err["errMsg"])
    except rave_exceptions.IncompletePaymentDetailsError as e:
        raise error.BadDataError(detail=e.err["errMsg"])


def charge_verification(data_in: dict):
    try:
        response = rave.Card.validate(data_in.get("flwRef", data_in.get("otp")))
        data_out = schemas.IPaymentValidationResponse(**response)
        return data_out
    except rave_exceptions.TransactionValidationError as e:
        raise error.BadDataError(detail=e.err["errMsg"])


def verify_payment(txRef: str):
    try:
        response = rave.Card.verify(txRef)
        data_out = schemas.IPaymentVerificationResponse(**response)
        return data_out
    except rave_exceptions.TransactionValidationError as e:
        raise error.BadDataError(detail=e.err["errMsg"])


def refund_payment(data_in: dict):
    try:
        response = rave.Card.refund(
            data_in.get("flwRef", None), data_in.get("amount", None)
        )
        data_out = schemas.convert_to_pydantic(**response)
        return data_out
    except rave_exceptions.TransactionValidationError as e:
        raise error.BadDataError(detail=e.err["errMsg"])


class DecimalToFloat(BaseModel):
    original_price: float
    discount: float


def calculate_discount(
    original_price: condecimal(max_digits=10, decimal_places=2),
    promo_codes: t.Optional[t.List[ProductPromoCode]],
    quantity: int = 1,
) -> float:
    discount = 0.0
    if promo_codes:
        for promo in promo_codes:
            discount += promo.discount
    if int(discount) < 1:
        return original_price * quantity
    elif original_price and int(quantity) > 0:
        discounted_price = original_price - ((original_price * discount) / 100)
        return discounted_price


def get_product_total_price(items: t.List[OrderItem]) -> float:
    total_price: float = 0.0
    if items:
        for item in items:
            if item.selling_unit.price:
                total_price += calculate_discount(
                    item.selling_unit.price,
                    item.promo_codes,
                    quantity=item.quantity,
                )
        return total_price
