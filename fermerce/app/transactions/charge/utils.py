import typing as t
from fermerce.app.order.models import OrderItem
from fermerce.app.promo_code.models import ProductPromoCode


def calculate_discount(
    original_price: float,
    promo_codes: t.Optional[t.List[ProductPromoCode]],
    quantity: int = 1,
) -> float:
    discount = 0.0
    if promo_codes:
        for promo in promo_codes:
            discount += promo.discount

    if int(discount) < 0:
        return float(original_price * quantity)
    elif original_price and int(quantity) > 0:
        discounted_price = float(
            float(original_price) - (float(original_price) * discount)
        )
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
