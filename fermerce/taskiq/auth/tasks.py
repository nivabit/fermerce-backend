# from fermerce.taskiq.broker import broker
import time
from fermerce.app.users.auth import models
from fermerce.app.users.user.models import User


async def create_token(
    user_ip: str, refresh_token: str, access_token: str, user_id: str
):
    get_user = await User.get_or_none(pk=user_id)
    if get_user:
        check_token = await models.Auth.get_or_none(
            user=user_id, ip_address=user_ip
        )
        if check_token:
            await models.Auth.filter(user=get_user, ip_address=user_ip).update(
                **dict(
                    access_token=access_token,
                    refresh_token=refresh_token,
                )
            )
        else:
            await models.Auth.create(
                user=get_user,
                ip_address=user_ip,
                refresh_token=refresh_token,
                access_token=access_token,
            )
