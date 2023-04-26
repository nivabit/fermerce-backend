from enum import Enum


class PaymentMethod(str, Enum):
    CARD = "card"
    BANK = "bank"
    ADDRESS = "shipping_address"


class PaymentStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    failed = "failed"
    refunded = "refunded"
    complete = "complete"


class PaymentCurrency(str, Enum):
    NGN = "NGN"
    USD = "USD"
