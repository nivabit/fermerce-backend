import typing as t
import uuid
from fastapi import status
from fastapi import Response
from tortoise.expressions import Q
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import ITotalCount, IResponseMessage
from fermerce.app.users.user.models import User
from fermerce.app.users.permission.models import Permission
from fermerce.core.enum.sort_type import SearchType
from fermerce.lib.errors import error
from fermerce.app.users.staff import schemas, models


async def create(
    data_in=schemas.IStaffIn,
):
    check_user = await User.get_or_none(id=str(data_in.user_id)).select_related("staff")

    if not check_user:
        raise error.NotFoundError("User not found")
    if check_user.staff:
        raise error.DuplicateError("Staff already exist")
    new_Staff = await models.Staff.create(user=check_user)
    if new_Staff:
        return IResponseMessage(message="Staff account was created successfully")
    raise error.ServerError("Error staff account")


async def filter(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    load_related: bool = False,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
    is_active: bool = False,
    is_suspended: bool = False,
    is_archived: bool = False,
    search_type: SearchType = SearchType._and,
) -> t.List[models.Staff]:
    offset = (page - 1) * per_page
    limit = per_page

    # Query the model with the filter and pagination parameters.
    query = None
    if search_type == SearchType._or:
        query = models.Staff.filter(
            Q(is_active=is_active) | Q(is_archived=is_archived) | Q(is_suspended=is_suspended)
        )
    else:
        query = models.Staff.filter(
            Q(is_active=is_active),
            Q(is_suspended=is_suspended),
            Q(is_archived=is_archived),
            Q(is_suspended=is_suspended),
        )
    results = await models.Staff.filter()

    query = query.all().offset(offset).limit(limit)
    if sort_by == SortOrder.asc and bool(order_by):
        query = query.order_by(
            *[f"-{col}" for col in order_by.split(",") if col in models.Staff._meta.fields]
        )
    elif sort_by == SortOrder.desc and bool(order_by):
        query = query.order_by(
            *[f"{col}" for col in order_by.split(",") if col in models.Staff._meta.fields]
        )
    else:
        query = query.order_by("-id")
    if select:
        query = query.values(
            *[col.strip() for col in select.split(",") if col.strip() in models.Staff._meta.fields]
        )
        if load_related:
            select_list = []
            if models.Staff._meta.fk_fields:
                select_list = select_list.extend(",".join(models.Staff._meta.fk_fields))
            elif models.Staff._meta.m2m_fields:
                select_list = select_list.extend(",".join(models.Staff._meta.m2m_fields))
            query = query.select_related(select_list)
    results = await query

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


async def remove_staff_data(data_in: schemas.IRemoveStaff) -> None:
    staff_to_remove = await models.Staff.get_or_none(data_in.staff_id)
    if staff_to_remove:
        if data_in.permanent:
            await staff_to_remove.delete()
        else:
            await staff_to_remove.update_from_dict(dict(is_active=False, archived=True))
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise error.NotFoundError(f"Staff with staff_id {data_in.staff_id} does not exist")


async def get_staff_details(
    staff_id: str, load_related: bool = False
) -> t.Union[schemas.IStaffOutFull, schemas.IStaffOut]:
    query = models.Staff.get_or_none(id=staff_id)
    if load_related:
        query = query.prefetch_related(
            ",".join(models.Staff._meta.o2o_fields),
            ",".join(models.Staff._meta.m2m_fields),
        )
    staff = await query
    try:
        if load_related:
            return schemas.IStaffOutFull.from_orm(staff)
        return schemas.IStaffOut.from_orm(staff)

    except Exception as e:
        raise error.ServerError(f"Error getting staff data {str(e)}")
    raise error.NotFoundError("No staff with the provided credential")


async def get_total_Staffs():
    total_count = await models.Staff.all().count()
    return ITotalCount(count=total_count)


async def add_staff_permission(
    data_in: schemas.IStaffRoleUpdate,
) -> IResponseMessage:
    get_staff = await models.Staff.get_or_none(id=data_in.staff_id)
    if not get_staff:
        raise error.NotFoundError("Staff not found")
    get_perms = await Permission.filter(id__in=data_in.permissions).all()
    existed_perm = []
    if not get_perms:
        raise error.NotFoundError("permissions not found")
    for permission in get_perms:
        if permission in await get_staff.permissions.all():
            existed_perm.append(permission.name)
            get_perms.remove(permission)
    if existed_perm:
        raise error.DuplicateError(f"Permission `{','.join(existed_perm)}` already exists")
    await get_staff.permissions.add(*get_perms)
    return IResponseMessage(message="Staff permission was updated successfully")


async def get_staff_permissions(
    staff_id: uuid.UUID,
) -> t.List[Permission]:
    check_Staff = await models.Staff.get_or_none(id=staff_id).select_related("permissions")
    if check_Staff:
        return await check_Staff.permissions.all()
    raise error.NotFoundError("Staff not found")


async def remove_staff_permissions(
    data_in: schemas.IStaffRoleUpdate,
) -> IResponseMessage:
    get_staff = await models.Staff.get_or_none(id=data_in.staff_id)

    if not get_staff:
        raise error.NotFoundError("Staff not found")
    check_perms = await Permission.filter(id__in=data_in.permissions)
    if not check_perms:
        raise error.NotFoundError(detail=" Permissions not found")
    await get_staff.permissions.remove(*check_perms)
    return IResponseMessage(message="Staff role was updated successfully")
