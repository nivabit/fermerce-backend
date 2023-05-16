from fastapi import Depends
from fermerce.lib.shared.dependency import AppAuth, AppWrite
from fermerce.app.users.staff.models import Staff
from fermerce.lib.errors import error
from fermerce.app.users.user.dependency import require_user


async def require_admin(get_user: dict = Depends(AppAuth.authenticate)):
    staff = await Staff.get_or_none(user=get_user.get("user_id", None))
    if staff:
        perm = await staff.permissions.filter(name="admin")
        if perm:
            return staff
    raise error.UnauthorizedError()


async def require_dispatcher(get_user: dict = Depends(AppAuth.authenticate)):
    staff = await Staff.get_or_none(user=get_user.get("user_id", None))
    if staff:
        perm = await staff.permissions.filter(name="dispatcher")
        if perm:
            return staff
    raise error.UnauthorizedError()


async def require_super_admin(get_user: dict = Depends(AppAuth.authenticate)):
    staff = await Staff.get_or_none(user=get_user.get("user_id", None))
    if staff:
        perm = await staff.permissions.filter(name="super_admin")
        if perm:
            return staff
    raise error.UnauthorizedError()


async def require_super_admin_or_admin(
    get_user: dict = Depends(AppAuth.authenticate),
):
    staff = await Staff.get_or_none(user=get_user.get("user_id", None))
    if staff:
        perm = await staff.permissions.filter(name__in=["super_admin", "admin"])
        if perm:
            return staff
    raise error.UnauthorizedError()
