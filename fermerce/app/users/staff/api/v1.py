import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.users.permission.schemas import IPermissionOut
from fermerce.app.users.staff import schemas, services, dependency
from fermerce.app.users.user.dependency import require_user
from fermerce.app.users.staff.dependency import require_admin
from fermerce.app.users.user.models import User

from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import IResponseMessage, ITotalCount
from fermerce.core.enum.sort_type import SearchType


router = APIRouter(prefix="/staff", tags=["Staff"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=IResponseMessage,
    # dependencies=[Depends(dependency.require_super_admin_or_admin)],
)
async def create_staff(data_in: schemas.IStaffIn) -> IResponseMessage:
    return await services.create(data_in=data_in)


@router.get("/", status_code=status.HTTP_200_OK, response_model=schemas.IStaffOutList)
async def get_staff_list(
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter through all attributes"
    ),
    select: t.Optional[str] = Query(
        default="", alias="select", description="select specific attributes"
    ),
    per_page: int = 10,
    page: int = 1,
    sort_by: t.Optional[SortOrder] = Query(
        default=SortOrder.desc, description="order by attribute, e.g. id"
    ),
    order_by: t.Optional[str] = Query(
        default="id", description="order by attribute, e.g. id"
    ),
    is_active: t.Optional[bool] = True,
    is_suspended: t.Optional[bool] = False,
    is_archived: t.Optional[bool] = False,
    search_type: t.Optional[SearchType] = SearchType._and,
    load_related: t.Optional[bool] = False,
):
    return await services.filter(
        filter_string=filter_string,
        per_page=per_page,
        page=page,
        select=select,
        sort_by=sort_by,
        order_by=order_by,
        is_active=is_active,
        is_suspended=is_suspended,
        is_archived=is_archived,
        search_type=search_type,
        load_related=load_related,
    )


@router.get(
    "/total/count",
    response_model=ITotalCount,
    # dependencies=[Depends(dependency.require_super_admin_or_admin)],
)
async def get_total_staff() -> ITotalCount:
    return await services.get_total_Staffs()


@router.get(
    "/{staff_id}/permissions",
    response_model=t.List[IPermissionOut],
    # dependencies=[Depends(dependency.require_super_admin_or_admin)],
)
async def get_staff_permissions(
    staff_id: uuid.UUID,
):
    return await services.get_staff_permissions(staff_id)


@router.put(
    "/permissions",
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(dependency.require_super_admin_or_admin)],
)
async def update_staff_permissions(
    data_in: schemas.IStaffRoleUpdate,
) -> IResponseMessage:
    return await services.add_staff_permission(data_in=data_in)


@router.delete(
    "/permissions",
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(dependency.require_super_admin)],
)
async def remove_staff_permissions(
    data_in: schemas.IStaffRoleUpdate,
) -> IResponseMessage:
    return await services.remove_staff_permissions(data_in=data_in)


@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(dependency.require_super_admin)],
)
async def delete_staff(data_in: schemas.IRemoveStaff) -> None:
    return await services.remove_staff_data(data_in)


@router.get("/details", status_code=status.HTTP_200_OK)
async def get_single_staff(
    user: User = Depends(require_user),
    load_related: bool = False,
):
    return await services.get_staff_details(user=user, load_related=load_related)


@router.get(
    "/{staff_id}/details",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependency.require_super_admin_or_admin)],
)
async def get_single_staff(
    staff_id: uuid.UUID,
    load_related: bool = False,
):
    return await services.get_staff(staff_id, load_related)
