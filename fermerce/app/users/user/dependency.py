from fastapi import Depends

from fermerce.lib.shared.dependency import AppAuth, AppWrite
from fermerce.app.users.user.models import User


__users_write = AppWrite(model=User)


async def require_user(get_user: dict = Depends(AppAuth.authenticate)):
    return await __users_write.get_user_data(user_id=get_user.get("user_id", None))
