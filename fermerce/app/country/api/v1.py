import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status
from fermerce.core.schemas.response import ITotalCount
from fermerce.app.country import schemas, services
from fermerce.core.enum.sort_type import SortOrder

# from fermerce.app.staff.dependency import require_super_admin_or_admin


router = APIRouter(prefix="/countries", tags=["Country"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def create_country(
    data_in: schemas.ICountryIn,
) -> schemas.ICountryOut:
    return await services.create(data_in=data_in)


@router.get(
    "/",
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_country_list(
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
    "/{country_id}",
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_country(country_id: uuid.UUID) -> schemas.ICountryOut:
    return await services.get(country_id=country_id)


@router.put(
    "/{country_id}",
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def update_country(
    country_id: uuid.UUID, type: schemas.ICountryIn
) -> schemas.ICountryOut:
    return await services.update(country_id=country_id, data_in=type)


@router.get(
    "/total/count",
    response_model=ITotalCount,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_total_country() -> t.Optional[ITotalCount]:
    return await services.get_total_count()


@router.delete(
    "/{country_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(require_super_admin_or_admin)],
)
async def delete_country(country_id: uuid.UUID) -> None:
    return await services.delete(country_id=country_id)
