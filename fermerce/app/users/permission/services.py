import uuid
import typing as t
from fastapi import status
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import ITotalCount
from fermerce.core.services.base import filter_and_list
from fermerce.lib.errors import error
from fermerce.app.users.permission import schemas, models
from fastapi import Response


# create permission
async def create(
    data_in: schemas.IPermissionIn,
) -> models.Permission:
    check_permission = await models.Permission.get_or_none(name=data_in.name)
    if check_permission:
        raise error.DuplicateError("permission already exists")
    new_type = await models.Permission.create(**data_in.dict())
    if not new_type:
        raise error.ServerError("Internal server error")
    return new_type


async def get(
    permission_id: uuid.UUID,
) -> models.Permission:
    perm = await models.Permission.get_or_none(id=permission_id)
    if not perm:
        raise error.NotFoundError("permission not found")
    return perm


# # get all permissions
async def filter(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
) -> t.List[models.Permission]:
    query = models.Permission

    if filter_string:
        query = query.filter(name__icontains=filter_string)
    return await filter_and_list(
        query=query,
        model=models.Permission,
        per_page=per_page,
        page=page,
        sort_by=sort_by,
        order_by=order_by,
        select=select,
    )


async def get_total_count() -> ITotalCount:
    total = await models.Permission.all().count()
    return ITotalCount(count=total).dict()


# # update permission
async def update(
    permission_id: uuid.UUID,
    data_in: schemas.IPermissionIn,
) -> models.Permission:
    check_permission = await models.Permission.get_or_none(id=permission_id)
    if not check_permission:
        raise error.NotFoundError("permission does not exist")
    check_name = await models.Permission.get_or_none(name=data_in.name)
    if check_name and check_name.id != permission_id:
        raise error.DuplicateError("permission already exists")
    elif check_name and check_name.id == permission_id:
        return check_permission
    await check_permission.update_from_dict(data_in.dict())
    return check_permission


# # delete permission
async def delete(
    permission_id: uuid.UUID,
) -> None:
    deleted_permission = await models.Permission.filter(
        id=permission_id
    ).delete()
    if not deleted_permission:
        raise error.NotFoundError("permission does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
