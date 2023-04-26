import uuid
import typing as t
from fastapi import status
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import ITotalCount
from fermerce.lib.errors import error
from fermerce.app.markets.status import schemas, models
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
    offset = (page - 1) * per_page
    limit = per_page

    # Construct a Q object to filter the results by the filter string.
    # filter_q = Q()

    # for field in models.Status._meta.fields_map.values():
    #     if field.internal:
    #         continue
    #     if field.unique:
    #         filter_q |= Q(**{f"{field.name}": filter_string})
    #     elif field.__class__.__name__ == "TextField":
    #         filter_q |= Q(**{f"{field.name}__icontains": filter_string})
    #     elif field.__class__.__name__ in ["CharField", "ForeignKeyField"]:
    #         filter_q |= Q(**{f"{field.name}__icontains": filter_string})

    # Query the model with the filter and pagination parameters.
    results = await models.Status.all().offset(offset).limit(limit)

    # Count the total number of results with the same filter.

    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if (offset + limit) < len(results) else None

    # Return the pagination information and results as a dictionary
    return {
        "previous": prev_page,
        "next": next_page,
        "total_results": len(results),
        "results": results,
    }


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
    await check_status.update_from_dict(data_in.dict())
    return check_status


# # delete permission
async def delete(
    status_id: uuid.UUID,
) -> None:
    deleted_status = await models.Status.filter(id=status_id).delete()
    if not deleted_status:
        raise error.NotFoundError("status does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
