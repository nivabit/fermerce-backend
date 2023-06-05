import typing as t
import uuid
from fastapi import BackgroundTasks, Request
from fermerce.core.schemas.response import IResponseMessage
from fermerce.lib.errors import error
from fermerce.app.auth import schemas, models
from fermerce.lib.utils.security import JWTAUTH
from fermerce.taskiq.auth.tasks import create_token


async def login(
    request: Request,
    task: BackgroundTasks,
    user_id: uuid.UUID,
) -> t.Union[schemas.IToken, IResponseMessage]:
    get_jwt_data_for_encode = schemas.IToEncode(user_id=str(user_id))
    access_token, refresh_token = JWTAUTH.jwt_encoder(
        data=get_jwt_data_for_encode.dict()
    )
    if access_token and refresh_token:
        user_ip = models.Auth.get_user_ip(request)
        task.add_task(
            create_token,
            owner_id=str(user_id),
            access_token=access_token,
            refresh_token=refresh_token,
            user_ip=user_ip,
        )
        return schemas.IToken(
            refresh_token=refresh_token, access_token=access_token
        )
    raise error.ServerError("Count not authenticate user")


async def login_token_refresh(
    data_in: schemas.IRefreshToken, request: Request, task: BackgroundTasks
) -> schemas.IToken:
    check_auth_token = await models.Auth.get_or_none(
        refresh_token=data_in.refresh_token
    )
    if not check_auth_token:
        raise error.UnauthorizedError()
    user_ip: str = models.Auth.get_user_ip(request)
    JWTAUTH.data_decoder(encoded_data=data_in.refresh_token)
    if check_auth_token.ip_address != user_ip:
        raise error.UnauthorizedError()
    get_jwt_data_for_encode = schemas.IToEncode(
        user_id=str(check_auth_token.owner_id)
    )
    access_token, refresh_token = JWTAUTH.jwt_encoder(
        data=get_jwt_data_for_encode.dict()
    )
    if access_token and refresh_token:
        task.add_task(
            create_token,
            owner_id=str(check_auth_token.owner_id),
            access_token=access_token,
            refresh_token=refresh_token,
            user_ip=user_ip,
        )
        return schemas.IToken(
            refresh_token=refresh_token, access_token=access_token
        )
    raise error.ServerError("could not create token, please try again")
