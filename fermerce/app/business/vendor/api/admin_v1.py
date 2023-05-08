import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.business.vendor import schemas, services

# from src.app.users.staff import dependency
from fermerce.core.enum.sort_type import SearchType, SortOrder
from fermerce.core.schemas.response import ITotalCount


router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.get(
    "/",
    response_model=schemas.IVendorListOut
    # dependencies=[Depends(dependency.require_super_admin_or_admin)],
)
async def get_users_list(
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
async def get_total_users() -> ITotalCount:
    return await services.get_total_Vendors()


@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(dependency.require_super_admin)],
)
async def delete_vendor(data_in: schemas.IRemoveVendor) -> None:
    return await services.remove_vendor_data(data_in=data_in)
