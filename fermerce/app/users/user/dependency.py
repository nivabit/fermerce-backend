from fastapi import Depends
import tortoise
from fermerce.lib.shared.dependency import AppAuth, AppWrite
from fermerce.app.users.user.models import User
from fermerce.lib.errors import error

__users_write = AppWrite(model=User)


async def require_user(get_user: dict = Depends(AppAuth.authenticate)):
    return await __users_write.get_user_data(user_id=get_user.get("user_id", None))


async def require_vendor(get_user: dict = Depends(AppAuth.authenticate)):
    user = await __users_write.get_user_data(user_id=get_user.get("user_id", None))
    try:
        if not user.vendor:
            raise error.UnauthorizedError()
        return user
    except tortoise.exceptions.NoValuesFetched:
        raise error.UnauthorizedError()
