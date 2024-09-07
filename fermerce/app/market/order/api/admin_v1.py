import typing as t
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.order import schemas, services
from fermerce.app.staff.dependency import (
    require_super_admin_or_admin,
    require_dispatcher,
)
from fermerce.core.enum.sort_type import SortOrder


router = APIRouter(prefix="/orders", tags=["orders"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_all_orders(
    user=None,
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
):
    return await services.filter(
        filter_string=filter_string,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order_by=order_by,
    )


@router.put(
    "/",
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(require_dispatcher)],
)
async def update_order_status(data_in: schemas.IOrderUpdate):
    return await services.update_order_status(data_in=data_in)
