import typing as t
import uuid
from fermerce.lib.paystack.verification.schemas import IBankAccountValidateIn
import pydantic as pyd


class IBankIn(IBankAccountValidateIn):
    vendor_id: uuid.UUID
    bvn: str
