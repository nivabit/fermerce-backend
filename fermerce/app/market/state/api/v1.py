import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status
from fermerce.core.schemas.response import ITotalCount
from fermerce.app.state import schemas, services
from fermerce.core.enum.sort_type import SortOrder

# from fermerce.app.staff.dependency import require_super_admin_or_admin


router = APIRouter(prefix="/states", tags=["State"])


@router.post(
    "/",
    # response_model=schemas.IStateOut,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def create_state(
    data_in: schemas.IStateIn,
) -> schemas.IStateOut:
    return await services.create(data_in=data_in)


@router.get(
    "/",
    response_model=schemas.IStateOutList,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_state_list(
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all shipping_address"
    ),
    select: t.Optional[str] = Query(
        default="",
        alias="select",
        description="specific attributes of the states",
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
    "/{state_id}",
    # response_model=schemas.IStateOut,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_state(state_id: uuid.UUID) -> schemas.IStateOut:
    return await services.get(state_id=state_id)


@router.put(
    "/{state_id}",
    response_model=schemas.IStateOut,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def update_state(
    state_id: uuid.UUID, type: schemas.IStateIn
) -> schemas.IStateOut:
    return await services.update(state_id=state_id, data_in=type)


@router.get(
    "/total/count",
    response_model=ITotalCount,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_total_state() -> t.Optional[ITotalCount]:
    return await services.get_total_count()


@router.delete(
    "/{state_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def delete_state(state_id: uuid.UUID) -> None:
    return await services.delete(state_id=state_id)
