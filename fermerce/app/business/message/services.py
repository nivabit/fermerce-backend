import uuid
import typing as t
from fastapi import status, Response
from tortoise.expressions import Q
from fermerce.app.business.vendor.models import Vendor
from fermerce.app.users.staff.models import Staff
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error
from fermerce.app.business.message import models, schemas


async def create(data_in: schemas.IMessageIn, staff: Staff) -> models.Message:
    get_vendor = await Vendor.get_or_none(id=data_in.vendor_id)
    if not get_vendor:
        raise error.NotFoundError("Vendor not found")
    new_message = await models.Message.create(
        sender=staff, message=data_in.message, vendor=get_vendor
    )
    if new_message:
        return new_message
    raise error.ServerError("Error while creating message")


async def update(
    message_id: uuid.UUID, data_in: schemas.IMessageIn, staff: Staff
) -> models.Message:
    get_message = await models.Message.get_or_none(
        id=message_id, vendor__id=data_in.vendor_id
    )
    if not get_message:
        raise error.NotFoundError("message not found")
    if get_message:
        get_message.update_from_dict(message=data_in.message, sender=staff)
        await get_message.save()
        return get_message
    raise error.ServerError("error updating message")


async def get(message_id: uuid.UUID, load_related: bool = False) -> models.Message:
    query = models.Message.filter(id=message_id)
    result = await filter_and_single(
        model=models.Message,
        query=query,
        load_related=load_related,
    )
    if not result:
        raise error.BadDataError("message not found")
    return result


async def filter(
    vendor_id: uuid.UUID,
    per_page: int = 10,
    page: int = 1,
    select: str = "",
    load_related: bool = False,
    filter_string: str = None,
    sort_by: SortOrder = SortOrder.desc,
    order_by: str = "created_at",
) -> t.List[models.Message]:
    query = models.Message.filter(vendor__id=vendor_id)
    if filter_string:
        query = query.filter(Q(message__icontains=filter_string))
    results = await filter_and_list(
        model=models.Message,
        query=query,
        per_page=per_page,
        page=page,
        select=select,
        order_by=order_by,
        sort_by=sort_by,
        load_related=load_related,
    )
    return results


async def delete(message_id: uuid.UUID) -> Response:
    get_message = await models.Message.get_or_none(id=message_id)
    if not get_message:
        raise error.NotFoundError("message not found")
    await get_message.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
