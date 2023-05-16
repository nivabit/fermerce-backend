import typing as t
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.markets.order import schemas, services
from fermerce.app.users.user.models import User
from fermerce.core.enum.sort_type import SortOrder
from fermerce.app.users.user.dependency import require_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_order(data_in: schemas.IOrderIn, user: User = Depends(require_user)):
    return await services.create(data_in=data_in, user=user)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_orders(
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all shipping_address"
    ),
    per_page: int = 10,
    page: int = 1,
    sort_by: t.Optional[SortOrder] = Query(
        default=SortOrder.desc, description="order by attribute, e.g. id"
    ),
    order_by: t.Optional[str] = Query(
        default="id", description="order by attribute, e.g. id"
    ),
    select: t.Optional[str] = Query(
        default="id", description="select order direct attributes, e.g. id"
    ),
    user: User = Depends(require_user),
    load_related: bool = False,
):
    return await services.filter(
        filter_string=filter_string,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order_by=order_by,
        user=user,
        select=select,
        load_related=load_related,
    )


@router.get("/{order_id}")
async def get_order(order_id: str, user: User = Depends(require_user)):
    return await services.get_order(order_id=order_id, user=user)


@router.get("/{order_id}/items")
async def get_order_items(order_id: str, user: User = Depends(require_user)):
    return await services.get_order_items(order_id=order_id, user=user)
