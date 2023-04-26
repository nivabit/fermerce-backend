import uuid
import typing as t
from fastapi import status
from fermerce.core.schemas.response import ITotalCount
from fermerce.lib.errors import error
from fermerce.app.products.measuring_unit import schemas, models
from fastapi import Response


async def create(
    data_in: schemas.IMeasuringUnitIn,
) -> models.MeasuringUnit:
    check_measuring_unit = await models.MeasuringUnit.get_or_none(unit=data_in.unit)
    if check_measuring_unit:
        raise error.DuplicateError("measuring unit already exists")
    new_type = await models.MeasuringUnit.create(**data_in.dict())
    if not new_type:
        raise error.ServerError("Internal server error")
    return new_type


async def get(
    unit_id: uuid.UUID,
) -> models.MeasuringUnit:
    perm = await models.MeasuringUnit.get_or_none(id=unit_id)
    if not perm:
        raise error.NotFoundError("measuring unit not found")
    return perm


async def filter(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
) -> t.List[models.MeasuringUnit]:
    query = models.MeasuringUnit
    if filter_string:
        query = query.filter(unit__icontains=filter_string)
    offset = (page - 1) * per_page
    limit = per_page
    results = await query.all().offset(offset).limit(limit)
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (offset + limit) < len(results) else None
    return {
        "previous": prev_page,
        "next": next_page,
        "total_results": len(results),
        "results": results,
    }


async def get_total_count() -> ITotalCount:
    total = await models.MeasuringUnit.all().count()
    return ITotalCount(count=total).dict()


async def update(
    unit_id: uuid.UUID,
    data_in: schemas.IMeasuringUnitIn,
) -> models.MeasuringUnit:
    check_measuring_unit = await models.MeasuringUnit.get_or_none(id=unit_id)
    if not check_measuring_unit:
        raise error.NotFoundError("measuring unit does not exist")
    check_unit = await models.MeasuringUnit.get_or_none(unit=data_in.unit)
    if check_unit and check_unit.id != unit_id:
        raise error.DuplicateError("measuring unit already exists")
    elif check_unit and check_unit.unit == check_measuring_unit.unit:
        return check_measuring_unit
    await models.MeasuringUnit.filter(id=unit_id).update(**data_in.dict())
    return check_measuring_unit


async def delete(
    unit_id: uuid.UUID,
) -> None:
    deleted_measuring_unit = await models.MeasuringUnit.filter(id=unit_id).delete()
    if not deleted_measuring_unit:
        raise error.NotFoundError("measuring unit does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
