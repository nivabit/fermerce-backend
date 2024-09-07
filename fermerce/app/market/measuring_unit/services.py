import uuid
import typing as t
from fastapi import status
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import ITotalCount
from fermerce.core.services.base_old import filter_and_list
from fermerce.lib.exceptions import exceptions
from fermerce.app.measuring_unit import schemas, models
from fastapi import Response


async def create(
    data_in: schemas.IMeasuringUnitIn,
) -> models.MeasuringUnit:
    check_measuring_unit = await models.MeasuringUnit.get_or_none(
        unit=data_in.unit
    )
    if check_measuring_unit:
        raise exceptions.DuplicateError("measuring unit already exists")
    new_type = await models.MeasuringUnit.create(**data_in.dict())
    if not new_type:
        raise exceptions.ServerError("Internal server error")
    return new_type


async def get(
    unit_id: uuid.UUID,
) -> models.MeasuringUnit:
    perm = await models.MeasuringUnit.get_or_none(id=unit_id)
    if not perm:
        raise exceptions.NotFoundError("measuring unit not found")
    return perm


async def filter(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = None,
    order_by: str = None,
    sort_by: SortOrder = SortOrder.asc,
) -> t.List[models.MeasuringUnit]:
    query = models.MeasuringUnit
    if filter_string:
        query = query.filter(unit__icontains=filter_string)
    results = await filter_and_list(
        model=models.MeasuringUnit,
        query=query,
        per_page=per_page,
        page=page,
        select=select,
        sort_by=sort_by,
        order_by=order_by,
    )
    return results


async def get_total_count() -> ITotalCount:
    total = await models.MeasuringUnit.all().count()
    return ITotalCount(count=total).dict()


async def update(
    unit_id: uuid.UUID,
    data_in: schemas.IMeasuringUnitIn,
) -> models.MeasuringUnit:
    check_measuring_unit = await models.MeasuringUnit.get_or_none(id=unit_id)
    if not check_measuring_unit:
        raise exceptions.NotFoundError("measuring unit does not exist")
    check_unit = await models.MeasuringUnit.get_or_none(unit=data_in.unit)
    if check_unit and check_unit.id != unit_id:
        raise exceptions.DuplicateError("measuring unit already exists")
    elif check_unit and check_unit.unit == check_measuring_unit.unit:
        return check_measuring_unit
    check_measuring_unit.update_from_dict(data_in.dict())
    await check_measuring_unit.save()
    return check_measuring_unit


async def delete(
    unit_id: uuid.UUID,
) -> None:
    deleted_measuring_unit = await models.MeasuringUnit.filter(
        id=unit_id
    ).delete()
    if not deleted_measuring_unit:
        raise exceptions.NotFoundError("measuring unit does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
