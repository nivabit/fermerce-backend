import json
import typing as t
import datetime
from fastapi.background import BackgroundTasks
from fastapi import Response, Request
from fermerce.core.settings import config
from fermerce.app.auth import schema
from fermerce.app.auth.repository import auth_token_repo
from fermerce.lib.utils.security import JWTAUTH
from fermerce.core.repository.base import ModelType


def create_response_cookies(
    user: ModelType, background_task: BackgroundTasks, request: Request
) -> t.Union[Response, bool]:
    get_jwt_data_for_encode = schema.IToEncode(user_id=str(user.id))
    access_token, refresh_token = JWTAUTH.jwt_encoder(data=get_jwt_data_for_encode.dict())

    if access_token and refresh_token:
        background_task.add_task(
            auth_token_repo.create,
            user_id=user.id,
            request=request,
            refresh_token=refresh_token,
            access_token=access_token,
        )

        response = Response(
            content=json.dumps(
                schema.IToken(
                    refresh_token=refresh_token,
                    access_token=access_token,
                ).dict()
            ),
            status_code=200,
            media_type="application/json",
        )
        response.set_cookie(
            key="auth_access_token",
            value=access_token,
            secure=True,
            httponly=config.debug,
            samesite="lax",
            max_age=config.access_token_expire_time,
            # expires=datetime.datetime.now() + config.get_access_expires_time(),
        )
        response.set_cookie(
            key="auth_refresh_token",
            value=refresh_token,
            secure=True,
            httponly=config.debug,
            samesite="lax",
            # expires=datetime.datetime.now() + config.get_refresh_expires_time(),
            max_age=config.refresh_token_expire_time,
        )
        return response
    return False


def update_response_cookies(
    user: ModelType, background_task: BackgroundTasks, request: Request
) -> t.Union[Request, bool]:
    get_jwt_data_for_encode = schema.IToEncode(user_id=str(user.id))
    access_token, refresh_token = JWTAUTH.jwt_encoder(data=get_jwt_data_for_encode.dict())
    if access_token and refresh_token:
        background_task.add_task(
            auth_token_repo.create,
            user=user,
            request=request,
            refresh_token=refresh_token,
            access_token=access_token,
        )

        request.cookies.update(
            key="auth_access_token",
            value=access_token,
            secure=True,
            httponly=config.debug,
            samesite="lax",
            max_age=config.access_token_expire_time,
            expires=datetime.datetime.now() + config.get_access_expires_time(),
        )
        request.cookies.update(
            key="auth_refresh_token",
            value=refresh_token,
            secure=True,
            httponly=config.debug,
            samesite="lax",
            expires=datetime.datetime.now() + config.get_refresh_expires_time(),
            max_age=config.refresh_token_expire_time,
        )
        return request

    else:
        return False
