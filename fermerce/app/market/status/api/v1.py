import typing as t
from fastapi import APIRouter, status, Query
from fermerce.core.enum.sort_type import SortOrder
from fermerce.app.status import services, schemas

# schemas,


router = APIRouter(prefix="/status", tags=["Status"])


@router.get(
    "/",
    response_model=schemas.IStatusOutList,
    status_code=status.HTTP_200_OK,
)
async def get_status_list(
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all attributes"
    ),
    select: t.Optional[str] = Query(
        default="",
        alias="select",
        description="specific attributes",
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
        sort_by=sort_by,
        order_by=order_by,
    )
