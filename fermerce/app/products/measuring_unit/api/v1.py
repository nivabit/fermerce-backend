import typing as t
import uuid
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.products.measuring_unit import services
from fermerce.core.schemas.response import ITotalCount
from fermerce.app.products.measuring_unit import schemas
from fermerce.app.users.staff.dependency import require_super_admin_or_admin


router = APIRouter(prefix="/measurements", tags=["Product measuring unit"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_super_admin_or_admin)],
)
async def create_measuring_unit(data_in: schemas.IMeasuringUnitIn):
    return await services.create(data_in=data_in)


@router.get(
    "/",
    response_model=schemas.IMeasuringUnitOutList,
    dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_measuring_unit_list(
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all unit"
    ),
    per_page: int = 10,
    page: int = 1,
):
    return await services.pro(
        filter_string=filter_string,
        per_page=per_page,
        page=page,
    )


@router.get(
    "/{unit_id}",
    response_model=schemas.IMeasuringUnitOut,
    dependencies=[Depends(require_super_admin_or_admin)],
)
async def get_measuring_unit(unit_id: uuid.UUID) -> schemas.IMeasuringUnitOut:
    return await services.get(unit_id=unit_id)


@router.put(
    "/{unit_id}",
    response_model=schemas.IMeasuringUnitOut,
    dependencies=[Depends(require_super_admin_or_admin)],
)
async def update_measuring_unit(
    unit_id: uuid.UUID, measurement: schemas.IMeasuringUnitIn
) -> schemas.IMeasuringUnitOut:
    return await services.update(unit_id=unit_id, data_in=measurement)


@router.get("/total/count", response_model=ITotalCount)
async def get_total_measuring_unit() -> t.Optional[ITotalCount]:
    return await services.get_total_count()


@router.delete(
    "/{unit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_super_admin_or_admin)],
)
async def delete_measurement(unit_id: uuid.UUID) -> None:
    return await services.delete(unit_id=unit_id)
