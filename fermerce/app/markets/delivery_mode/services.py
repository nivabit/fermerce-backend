import uuid
import typing as t
from fastapi import status
from tortoise.expressions import Q
from fermerce.core.schemas.response import ITotalCount
from fermerce.lib.errors import error
from fermerce.app.markets.delivery_mode import schemas, models
from fastapi import Response


async def create(
    data_in: schemas.IDeliveryModeIn,
) -> models.DeliveryMode:
    check_delivery_mode = await models.DeliveryMode.get_or_none(name=data_in.name)
    if check_delivery_mode:
        raise error.DuplicateError("delivery type already exists")
    new_delivery_mode = await models.DeliveryMode.create(**data_in.dict())
    if not new_delivery_mode:
        raise error.ServerError("Internal server error")
    return new_delivery_mode


async def get(
    delivery_mode_id: uuid.UUID,
) -> models.DeliveryMode:
    delivery_mode = await models.DeliveryMode.get_or_none(id=delivery_mode_id)
    if not delivery_mode:
        raise error.NotFoundError("delivery type not found")
    return delivery_mode


async def filter(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
) -> t.List[models.DeliveryMode]:
    query = models.DeliveryMode
    if filter_string:
        query = query.filter(Q(name__icontains=filter_string))
    results = await query.all().offset(offset).limit(limit)
    offset = (page - 1) * per_page
    limit = per_page
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (offset + limit) < len(results) else None
    return {
        "previous": prev_page,
        "next": next_page,
        "total_results": len(results),
        "results": results,
    }


async def get_total_count() -> ITotalCount:
    total = await models.DeliveryMode.all().count()
    return ITotalCount(count=total).dict()


async def update(
    delivery_mode_id: uuid.UUID,
    data_in: schemas.IDeliveryModeIn,
) -> models.DeliveryMode:
    check_delivery_mode = await models.DeliveryMode.get_or_none(id=delivery_mode_id)
    if not check_delivery_mode:
        raise error.NotFoundError("delivery type does not exist")
    check_name = await models.DeliveryMode.get_or_none(name=data_in.name)
    if check_name and check_name.id != delivery_mode_id:
        raise error.DuplicateError("delivery type already exists")
    elif check_name and check_name.id == delivery_mode_id:
        return check_delivery_mode
    await check_delivery_mode.update_from_dict(data_in.dict())
    return check_delivery_mode


async def delete(
    delivery_mode_id: uuid.UUID,
) -> None:
    deleted_delivery_mode = await models.DeliveryMode.filter(id=delivery_mode_id).delete()
    if not deleted_delivery_mode:
        raise error.NotFoundError("delivery type does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
