import uuid
import typing as t
from fastapi import status
from tortoise.expressions import Q
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import ITotalCount
from fermerce.core.services.base import filter_and_list
from fermerce.lib.errors import error
from fermerce.app.status import schemas, models
from fastapi import Response


# create permission
async def create(
    data_in: schemas.IStatusIn,
) -> models.Status:
    check_status = await models.Status.get_or_none(name=data_in.name)
    if check_status:
        raise error.DuplicateError("status already exists")
    new_type = await models.Status.create(**data_in.dict())
    if not new_type:
        raise error.ServerError("Internal server error")
    return new_type


async def get(
    status_id: uuid.UUID,
) -> models.Status:
    perm = await models.Status.get_or_none(id=status_id)
    if not perm:
        raise error.NotFoundError("status not found")
    return perm


# # get all permissions
async def filter(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
) -> t.List[models.Status]:
    query = models.Status.filter(Q(name__icontains=filter_string))
    result = await filter_and_list(
        model=models.Status,
        query=query,
        per_page=per_page,
        page=page,
        order_by=order_by,
        select=select,
        sort_by=sort_by,
    )
    return result


async def get_total_count() -> ITotalCount:
    total = await models.Status.all().count()
    return ITotalCount(count=total).dict()


# # update permission
async def update(
    status_id: uuid.UUID,
    data_in: schemas.IStatusIn,
) -> models.Status:
    check_status = await models.Status.get_or_none(id=status_id)
    if not check_status:
        raise error.NotFoundError("status does not exist")
    check_name = await models.Status.get_or_none(name=data_in.name)
    if check_name and check_name.id != status_id:
        raise error.DuplicateError("status already exists")
    elif check_name and check_name.id == status_id:
        return check_status
    check_status.update_from_dict(data_in.dict())
    await check_status.save()
    return check_status


# # delete permission
async def delete(
    status_id: uuid.UUID,
) -> None:
    deleted_status = await models.Status.filter(id=status_id).delete()
    if not deleted_status:
        raise error.NotFoundError("status does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
