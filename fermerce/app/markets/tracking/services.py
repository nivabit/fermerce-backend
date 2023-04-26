import uuid
import typing as t
from fastapi import status, Response
from fermerce.app.markets.order.models import OrderItem
from fermerce.core.schemas.response import IResponseMessage
from fermerce.lib.errors import error
from fermerce.app.markets.tracking import models, schemas


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
        return IResponseMessage(message="track created successfully")
    raise error.ServerError("Error while creating track")


async def update(track_id: uuid.UUID, data_in: schemas.ITrackIn) -> models.Tracking:
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
    ).update(note=data_in.note, location=data_in.location)
    if result:
        return IResponseMessage(message="order item tracking was updated successfully")
    raise error.ServerError("error updating order item tracking")


async def get(track_id: uuid.UUID) -> models.Tracking:
    get_track = await models.Tracking.get_or_none(id=track_id)
    if not get_track:
        raise error.BadDataError("order item tracking not found")
    return get_track


async def filter(order_item_id: uuid.UUID) -> t.List[models.Tracking]:
    get_order_item = await OrderItem.get_or_none(id=order_item_id)
    if not get_order_item:
        raise error.NotFoundError("Order item not found")
    get_tracks = await models.Tracking.filter(order_item=order_item_id).all()
    return get_tracks


async def delete(track_id: uuid.UUID) -> Response:
    get_track = await models.Tracking.get_or_none(id=track_id)
    if not get_track:
        raise error.NotFoundError("order item Tracking not found")
    await get_track.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
