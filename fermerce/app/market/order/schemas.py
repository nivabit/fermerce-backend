import datetime
import typing as t
import uuid
import pydantic as pyd
from fermerce.app.address import schemas as address_schema
from fermerce.app.user import schemas as user_schema
from fermerce.app.state import schemas as state_schema
from fermerce.app.selling_units import schemas as selling_unit_schema


class IOrderOrderOut(pyd.BaseModel):
    id: uuid.UUID
    order_id: str
    user: user_schema.IUserOut
    shipping_address: address_schema.IAddressOut
    items: t.List["IOrderItemsOut"] = []
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class IOrderItemsOut(pyd.BaseModel):
    tracking_id: str
    quantity: int
    status: t.List[state_schema.IStateIn] = []
    # product: product_schema.IProductShortInfo
    selling_unit: selling_unit_schema.IProductSellingUnitIn


class IOrderSuccessOut(pyd.BaseModel):
    order_id: uuid.UUID


class IOrderIn(pyd.BaseModel):
    cart_ids: t.Optional[t.List[uuid.UUID]] = None
    delivery_mode: uuid.UUID
    address_id: uuid.UUID


class IOrderUpdate(pyd.BaseModel):
    tracking_id: str
    status_id: uuid.UUID


class IOrderUpdatePromoCodeIn(pyd.BaseModel):
    order_id: uuid.UUID
    promo_code: str


class IOrderItemUpdate(pyd.BaseModel):
    item_tracking_id: str
    delivered: bool = True
