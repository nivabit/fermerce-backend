import typing as t
from fastapi import BackgroundTasks, Request
from tortoise.expressions import Q
from fermerce.app.users.user.models import User
from fermerce.core.schemas.response import IResponseMessage
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fermerce.lib.errors import error
from fermerce.app.users.auth import schemas, models
from fermerce.lib.utils.security import JWTAUTH
from fermerce.taskiq.auth.tasks import create_token
from fermerce.taskiq.user import tasks


async def login(
    request: Request, data_in: OAuth2PasswordRequestForm, task: BackgroundTasks
) -> t.Union[schemas.IToken, IResponseMessage]:
    check_user = await User.get_or_none(
        Q(username__icontains=data_in.username) | Q(email=data_in.username)
    )
    if not check_user:
        raise error.UnauthorizedError(detail="incorrect email, username or password")
    if not check_user.check_password(data_in.password):
        raise error.UnauthorizedError(detail="incorrect email or password")
    if check_user.is_archived:
        raise error.UnauthorizedError()
    if check_user.is_suspended:
        raise error.UnauthorizedError("Your account is suspended")
    if not check_user.is_verified and check_user.is_active:
        await tasks.send_users_activation_email.kiq(
            dict(
                email=data_in.username,
                id=str(check_user.id),
                full_name=f"{check_user.firstname} {check_user.lastname}"
                if check_user.firstname and check_user.lastname
                else check_user.username,
            )
        )
        return IResponseMessage(
            message="Your is not verified, Please check your for verification link before continuing"
        )

    get_jwt_data_for_encode = schemas.IToEncode(user_id=str(check_user.id))
    access_token, refresh_token = JWTAUTH.jwt_encoder(
        data=get_jwt_data_for_encode.dict()
    )
    if access_token and refresh_token:
        user_ip = models.Auth.get_user_ip(request)
        task.add_task(
            create_token,
            user_id=str(check_user.id),
            access_token=access_token,
            refresh_token=refresh_token,
            user_ip=user_ip,
        )
        return schemas.IToken(refresh_token=refresh_token, access_token=access_token)
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
    get_jwt_data_for_encode = schemas.IToEncode(user_id=str(check_auth_token.user_id))
    access_token, refresh_token = JWTAUTH.jwt_encoder(
        data=get_jwt_data_for_encode.dict()
    )
    if access_token and refresh_token:
        task.add_task(
            create_token,
            user_id=check_auth_token.user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            user_ip=user_ip,
        )
        return schemas.IToken(refresh_token=refresh_token, access_token=access_token)
    raise error.ServerError("could not create token, please try again")
