import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.users.permission import schemas, services
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import ITotalCount


router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post(
    "/",
    response_model=schemas.IPermissionOut,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def create_permission(
    data_in: schemas.IPermissionIn,
) -> schemas.IPermissionOut:
    return await services.create(data_in=data_in)


@router.get(
    "/",
    # response_model=list[schemas.IPermissionOut],
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_permission_list(
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all shipping_address"
    ),
    select: t.Optional[str] = Query(
        default="",
        alias="select",
        description="specific attributes of the countries",
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
    "/{permission_id}",
    response_model=schemas.IPermissionOut,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_permission(permission_id: uuid.UUID) -> schemas.IPermissionOut:
    return await services.get(permission_id=permission_id)


@router.put(
    "/{permission_id}",
    response_model=schemas.IPermissionOut,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def update_permission(
    permission_id: uuid.UUID, permission: schemas.IPermissionIn
) -> schemas.IPermissionOut:
    return await services.update(
        permission_id=permission_id, data_in=permission
    )


@router.get(
    "/total/count",
    response_model=ITotalCount,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_total_permission() -> t.Optional[ITotalCount]:
    return await services.get_total_count()


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def delete_permission(permission_id: uuid.UUID) -> None:
    return await services.delete(permission_id=permission_id)
