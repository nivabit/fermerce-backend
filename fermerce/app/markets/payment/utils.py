import typing as t
from src.app.market.order.model import OrderItem
from src.app.market.payment import schema
import httpx
from rave_python import Rave
from core.settings import config
import warnings

from pydantic import condecimal, BaseModel


class DecimalToFloat(BaseModel):
    original_price: float
    discount: float


def calculate_discount(
    original_price: condecimal(max_digits=10, decimal_places=2),
    discount: float,
) -> float:
    data = DecimalToFloat(original_price=original_price, discount=discount)
    if int(discount) < 1:
        return original_price
    discounted_price = data.original_price - ((data.original_price * data.discount) / 100)
    return discounted_price


warnings.filterwarnings("ignore")
rave = Rave(
    publicKey=config.payment_public_key,
    secretKey=config.payment_secret_key,
    usingEnv=False,
    production=True,
)

payment_init_url: str = "https://api.flutterwave.com/v3/payments"


async def generate_link(
    data_in: schema.IPaymentLinkData,
) -> schema.IPaymentResponse:
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {config.payment_secret_key}"}
    ) as client:
        response = await client.post(
            url=f"{payment_init_url}",
            json=data_in.dict(),
        )
    return schema.IPaymentResponse(**response.json())


def verify_payment(tx_ref: str) -> schema.IPaymentVerifyOut:
    response: schema.IPaymentVerifyOut = rave.Card.verify(tx_ref)
    return schema.IPaymentVerifyOut(**response)


def get_product_total_price(
    items: t.List[OrderItem],
) -> float:
    if items:
        for item in items:
            if item.selling_unit.price:
                price += calculate_discount(
                    item.selling_unit.price, item.product.property.discount
                )
            hard_back_price += item.hard_back_qty * calculate_discount(
                item.product.property.hard_back_price, item.product.property.discount
            )
            paper_back_price += item.paper_back_qty * calculate_discount(
                item.product.property.paper_back_price, item.product.property.discount
            )
        total_price = pdf_price + hard_back_price + paper_back_price
        return total_price
