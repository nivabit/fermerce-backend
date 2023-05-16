import uuid
import typing as t
from fastapi import status, Response
from tortoise.expressions import Q
from fermerce.app.markets.order.models import OrderItem
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error
from fermerce.app.markets.tracking import models, schemas


# Todo: Make sure to check if the order that this item belongs to is payed for or not before they can add tracking
async def create(data_in: schemas.ITrackIn) -> models.Tracking:
    get_order_item = await OrderItem.get_or_none(
        tracking_id=data_in.order_item_tracking_id
    )
    if not get_order_item:
        raise error.NotFoundError("order item not found")
    new_track = await models.Tracking.create(
        order_item=get_order_item, location=data_in.location, note=data_in.note
    )
    if new_track:
        return new_track
    raise error.ServerError("Error while creating track")


# Todo: Make sure to check if the order that this item belongs to is payed for or not before they can add tracking
async def update(
    track_id: uuid.UUID, data_in: schemas.ITrackIn
) -> models.Tracking:
    get_order_item = await OrderItem.get_or_none(
        tracking_id=data_in.order_item_tracking_id
    )
    if not get_order_item:
        raise error.NotFoundError("order item not found")
    get_track = await models.Tracking.get_or_none(
        id=track_id,
        note=data_in.note,
        location=data_in.location,
        order_item=get_order_item,
    )
    if get_track:
        raise error.DuplicateError("tracking already exist for this order item")
    result = await models.Tracking.filter(
        id=track_id, order_item=get_order_item
    ).first()
    if not result:
        raise error.NotFoundError("Tracking is not found")
    if result:
        result.update_from_dict(**data_in)
        await result.save()
        return result
    raise error.ServerError("error updating order item tracking")


async def get(
    track_id: uuid.UUID, load_related: bool = False
) -> models.Tracking:
    query = models.Tracking.filter(id=track_id)
    result = await filter_and_single(
        model=models.Tracking,
        query=query,
        load_related=load_related,
    )
    if not result:
        raise error.BadDataError("order item tracking not found")
    return result


async def filter(
    order_item_id: str,
    per_page: int = 10,
    page: int = 1,
    select: str = "",
    load_related: bool = False,
    filter_string: str = None,
) -> t.List[models.Tracking]:
    query = models.Tracking.filter(order_item__tracking_id=order_item_id)
    if filter_string:
        query = query.filter(
            Q(location__icontains=filter_string)
            | Q(node__icontains=filter_string)
        )
    results = await filter_and_list(
        model=models.Tracking,
        query=query,
        per_page=per_page,
        page=page,
        select=select,
        load_related=load_related,
    )
    return results


async def delete(track_id: uuid.UUID) -> Response:
    get_track = await models.Tracking.get_or_none(id=track_id)
    if not get_track:
        raise error.NotFoundError("order item Tracking not found")
    await get_track.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
