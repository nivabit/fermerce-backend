import typing as t
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fermerce.app.user import dependency, schemas, services
from fermerce.core.schemas.response import IResponseMessage
from fermerce.app.user.models import User
from fermerce.lib.errors import error
from fermerce.app.auth import schemas as auth_schemas
from fermerce.app.user.api import USER_META

router = APIRouter(
    prefix=USER_META.get("router_prefix"), tags=[USER_META.get("tag")]
)
auth = APIRouter(
    prefix=f"{USER_META.get('router_prefix')}/auth", tags=[USER_META.get("tag")]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(data_in: schemas.IUserIn):
    return await services.create(data_in=data_in)


@router.get(
    "/me",
    response_model=t.Union[schemas.IUserOutFull, schemas.IUserOut],
    status_code=status.HTTP_200_OK,
)
async def get_users_current_data(
    user: dict = Depends(dependency.AppAuth.authenticate),
    load_related: bool = False,
) -> t.Union[schemas.IUserOutFull, schemas.IUserOut]:
    if not user.get("user_id", None):
        raise error.UnauthorizedError()
    return await services.get_user(
        user.get("user_id", None), load_related=load_related
    )


@auth.post("/password/reset-link", status_code=status.HTTP_200_OK)
async def reset_password_link(
    users_data: schemas.IGetPasswordResetLink,
) -> IResponseMessage:
    return await services.reset_password_link(users_data)


@router.put("/", status_code=status.HTTP_200_OK)
async def update_user_details(
    data_in: schemas.IUserUpdateIn,
) -> IResponseMessage:
    return await services.update_user_details(data_in)


@auth.post(
    "/login",
    response_model=t.Union[auth_schemas.IToken, IResponseMessage],
    status_code=status.HTTP_200_OK,
)
async def login(
    request: Request,
    task: BackgroundTasks,
    data_in: OAuth2PasswordRequestForm = Depends(),
) -> t.Union[auth_schemas.IToken, IResponseMessage]:
    result = await services.login(data_in=data_in, request=request, task=task)
    return result


@auth.post(
    "/token-refresh",
    response_model=auth_schemas.IToken,
    status_code=status.HTTP_200_OK,
)
async def login_token_refresh(
    data_in: auth_schemas.IRefreshToken,
    request: Request,
    task: BackgroundTasks,
):
    return await services.login_token_refresh(
        data_in=data_in,
        request=request,
        task=task,
    )


@auth.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_User_email(
    data_in: schemas.IUserAccountVerifyToken,
) -> IResponseMessage:
    return await services.verify_users_email(data_in)


@auth.put("/password/reset", status_code=status.HTTP_200_OK)
async def update_users_password(
    data_in: schemas.IUserResetPassword,
) -> IResponseMessage:
    return await services.update_user_password(data_in)


@auth.put("/password/no_token", status_code=status.HTTP_200_OK)
async def update_user_password_no_token(
    data_in: schemas.IUserResetPasswordNoToken,
    user_data: User = Depends(dependency.require_user),
) -> IResponseMessage:
    return await services.update_users_password_no_token(data_in, user_data)


@auth.post(
    "/check/dev",
    status_code=status.HTTP_200_OK,
    response_model=IResponseMessage,
)
async def check_user_email(
    data_in: schemas.ICheckUserEmail,
) -> IResponseMessage:
    return await services.check_user_email(data_in)
