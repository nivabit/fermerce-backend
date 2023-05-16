import uuid
import typing as t
from fastapi import APIRouter, Depends, Query, status
from fermerce.app.business.message import services, schemas
from fermerce.app.users.staff.dependency import require_super_admin_or_admin
from fermerce.app.users.staff.models import Staff
from fermerce.core.enum.sort_type import SortOrder

router = APIRouter(prefix="/messages", tags=["Message"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_message(
    data_in: schemas.IMessageIn,
    staff: Staff = Depends(require_super_admin_or_admin),
):
    return await services.create(data_in=data_in, staff=staff)


@router.put("/{message_id}", status_code=status.HTTP_200_OK)
async def update_message(
    message_id: uuid.UUID,
    data_in: schemas.IMessageIn,
    staff: Staff = Depends(require_super_admin_or_admin),
):
    return await services.update(
        message_id=message_id, data_in=data_in, staff=staff
    )


@router.get("/{message_id}", status_code=status.HTTP_200_OK)
async def create_message(message_id: uuid.UUID, load_related: bool = False):
    return await services.get(message_id=message_id, load_related=load_related)


@router.get("/vendor/{vendor_id}/", status_code=status.HTTP_200_OK)
async def get_messages(
    vendor_id: uuid.UUID,
    per_page: int = 10,
    page: int = 1,
    select: t.Optional[str] = Query(
        default="", description="select order direct attributes, e.g. id"
    ),
    filter_string: t.Optional[str] = Query(
        default="", alias="filter", description="filter all shipping_address"
    ),
    sort_by: t.Optional[SortOrder] = Query(
        default=SortOrder.desc, description="order by attribute, e.g. id"
    ),
    order_by: t.Optional[str] = Query(
        default="id", description="order by attribute, e.g. id"
    ),
    load_related: bool = False,
):
    return await services.filter(
        vendor_id=vendor_id,
        per_page=per_page,
        page=page,
        select=select,
        load_related=load_related,
        filter_string=filter_string,
        order_by=order_by,
        sort_by=sort_by,
    )


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    message_id: uuid.UUID, _: Staff = Depends(require_super_admin_or_admin)
) -> None:
    return await services.delete(
        message_id=message_id,
    )
