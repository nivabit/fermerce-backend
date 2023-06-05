import typing as t
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.recipient import services
from fermerce.app.staff import dependency
from fermerce.core.enum.sort_type import SortOrder


router = APIRouter(
    prefix="/bank_details",
    dependencies=[Depends(dependency.require_super_admin_or_admin)],
    tags=["Vendor business bank account"],
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_vendor_bank_detail_list(
    filter_string: t.Optional[str] = Query(
        default="",
        alias="filter",
        description="filter all refund by user email or payment reference",
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
    load_related: bool = False,
):
    return await services.list_bank_details_list(
        filter_string=filter_string,
        per_page=per_page,
        page=page,
        select=select,
        order_by=order_by,
        sort_by=sort_by,
        load_related=load_related,
    )
