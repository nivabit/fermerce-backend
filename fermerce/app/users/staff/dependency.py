from fastapi import Depends
from fermerce.lib.shared.dependency import AppAuth, AppWrite
from fermerce.app.users.staff.models import Staff
from fermerce.lib.errors import error

__staff_write = AppWrite(model=Staff)


async def require_admin(get_user: dict = Depends(AppAuth.authenticate)):
    staff = await __staff_write.current_user(
        user_id=get_user.get("user_id", None),
    )
    if staff.permissions.filter(staff=get_user.get("user_id", None), name="admin"):
        return staff
    raise error.UnauthorizedError()


async def require_dispatcher(get_user: dict = Depends(AppAuth.authenticate)):
    staff = await __staff_write.current_user(
        user_id=get_user.get("user_id", None),
    )
    if staff.permissions.filter(user=get_user.get("user_id", None), name="dispatcher"):
        return staff
    raise error.UnauthorizedError()


async def require_super_admin(get_user: dict = Depends(AppAuth.authenticate)):
    staff = await __staff_write.current_user(
        user_id=get_user.get("user_id", None),
    )
    if staff.permissions.filter(user=get_user.get("user_id", None), name="super_admin"):
        return staff
    raise error.UnauthorizedError()


async def require_super_admin_or_admin(get_user: dict = Depends(AppAuth.authenticate)):
    staff = await __staff_write.current_user(
        user_id=get_user.get("user_id", None),
    )
    if staff.permissions.filter(
        user=get_user.get("user_id", None), name__in__=["super_admin", "admin"]
    ):
        return staff
    raise error.UnauthorizedError()


async def require_staff_data_all(get_user: dict = Depends(AppAuth.authenticate)):
    staff = await __staff_write.get_user_data(user_id=get_user.get("user_id", None))
    return staff


async def require_staff_data(get_user: dict = Depends(AppAuth.authenticate)):
    data = await __staff_write.current_user(user_id=get_user.get("user_id", None))
    return data
