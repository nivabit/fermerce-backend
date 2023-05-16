import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status
from fermerce.core.schemas.response import ITotalCount
from fermerce.app.markets.delivery_mode import schemas, services
from fermerce.core.enum.sort_type import SortOrder

# from fermerce.app.users.staff.dependency import require_super_admin_or_admin


router = APIRouter(prefix="/delivery_modes", tags=["Order delivery modes"])


@router.post(
    "/",
    response_model=schemas.IDeliveryModeOut,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def create_delivery_mode(
    data_in: schemas.IDeliveryModeIn,
) -> schemas.IDeliveryModeOut:
    return await services.create(data_in=data_in)


@router.get(
    "/",
    response_model=schemas.IDeliveryModeList,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_delivery_mode_list(
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all shipping_address"
    ),
    select: t.Optional[str] = Query(
        default="",
        alias="select",
        description="specific attributes of the categories",
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
        per_page=per_page,
        page=page,
        select=select,
        order_by=order_by,
        sort_by=sort_by,
    )


@router.get(
    "/{delivery_mode_id}",
    # response_model=schemas.IDeliveryModeOut,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_delivery_mode(
    delivery_mode_id: uuid.UUID,
) -> schemas.IDeliveryModeOut:
    return await services.get(delivery_mode_id=delivery_mode_id)


@router.put(
    "/{delivery_mode_id}",
    response_model=schemas.IDeliveryModeOut,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def update_delivery_mode(
    delivery_mode_id: uuid.UUID, delivery_mode: schemas.IDeliveryModeIn
) -> schemas.IDeliveryModeOut:
    return await services.update(
        delivery_mode_id=delivery_mode_id, data_in=delivery_mode
    )


@router.get(
    "/total/count",
    response_model=ITotalCount,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_total_delivery_mode() -> t.Optional[ITotalCount]:
    return await services.get_total_count()


@router.delete(
    "/{delivery_mode_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def delete_delivery_mode(delivery_mode_id: uuid.UUID) -> None:
    return await services.delete(delivery_mode_id=delivery_mode_id)
