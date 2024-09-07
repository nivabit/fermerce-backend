# from fermerce.taskiq.broker import broker
import time
from fermerce.app.auth import models
from fermerce.app.user.models import User


async def create_token(
    user_ip: str,
    refresh_token: str,
    access_token: str,
    user_id: str,
):
    check_token = await models.Auth.get_or_none(
        owner_id=user_id,
        ip_address=user_ip,
    )
    if check_token:
        await check_token.update(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    else:
        await models.Auth.create(
            owner_di=user_id,
            ip_address=user_ip,
            refresh_token=refresh_token,
            access_token=access_token,
        )
