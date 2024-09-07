import uuid
import typing as t
from fastapi import status
from tortoise.expressions import Q
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import ITotalCount
from fermerce.core.services.base_old import filter_and_list
from fermerce.lib.exceptions import exceptions
from fermerce.app.state import schemas, models
from fastapi import Response


# create permission
async def create(
    data_in: schemas.IStateIn,
) -> models.State:
    check_state = await models.State.get_or_none(name=data_in.name)
    if check_state:
        raise exceptions.DuplicateError("state already exists")
    new_type = await models.State.create(**data_in.dict())
    if not new_type:
        raise exceptions.ServerError("Internal server error")
    return new_type


async def get(
    state_id: uuid.UUID,
) -> models.State:
    perm = await models.State.get_or_none(id=state_id)
    if not perm:
        raise exceptions.NotFoundError("state not found")
    return perm


# # get all permissions
async def filter(
    filter_string: str = None,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
) -> t.List[models.State]:
    query = models.State
    if filter_string:
        query = query.filter(name__icontains=filter_string)
    results = await filter_and_list(
        model=models.State,
        query=query,
        select=select,
        sort_by=sort_by,
        order_by=order_by,
        page=page,
        per_page=per_page,
    )
    return results


async def get_total_count() -> ITotalCount:
    total = await models.State.all().count()
    return ITotalCount(count=total).dict()


# # update permission
async def update(
    state_id: uuid.UUID,
    data_in: schemas.IStateIn,
) -> models.State:
    check_state = await models.State.get_or_none(id=state_id)
    if not check_state:
        raise exceptions.NotFoundError("state does not exist")
    check_name = await models.State.get_or_none(name=data_in.name)
    if check_name and check_name.id != state_id:
        raise exceptions.DuplicateError("state already exists")
    elif check_name and check_name.id == state_id:
        return check_state
    check_state.update_from_dict(data_in.dict())
    await check_state.save()

    return check_state


# # delete permission
async def delete(
    state_id: uuid.UUID,
) -> None:
    deleted_state = await models.State.filter(id=state_id).delete()
    if not deleted_state:
        raise exceptions.NotFoundError("state does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
