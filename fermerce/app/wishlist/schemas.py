import uuid
import pydantic as pyd


class IWishListIn(pyd.BaseModel):
    quantity: int = pyd.Field(default=1, gt=0)
    selling_unit: uuid.UUID
    product_id: uuid.UUID
