import typing as t
from fastapi import APIRouter, Depends, status
from fermerce.app.users.user import dependency, schemas, services
from fermerce.core.schemas.response import IResponseMessage
from fermerce.app.users.user.models import User
from fermerce.lib.errors import error


router = APIRouter(prefix="/users", tags=["Users"])


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


@router.post("/password/reset-link", status_code=status.HTTP_200_OK)
async def reset_password_link(
    users_data: schemas.IGetPasswordResetLink,
) -> IResponseMessage:
    return await services.reset_password_link(users_data)


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_User_email(
    data_in: schemas.IUserAccountVerifyToken,
) -> IResponseMessage:
    return await services.verify_users_email(data_in)


@router.put("/password/reset", status_code=status.HTTP_200_OK)
async def update_users_password(
    data_in: schemas.IUserResetPassword,
) -> IResponseMessage:
    return await services.update_user_password(data_in)


@router.put("/password/no_token", status_code=status.HTTP_200_OK)
async def update_user_password_no_token(
    data_in: schemas.IUserResetPasswordNoToken,
    user_data: User = Depends(dependency.require_user),
) -> IResponseMessage:
    return await services.update_users_password_no_token(data_in, user_data)


@router.post(
    "/check/dev",
    status_code=status.HTTP_200_OK,
    response_model=IResponseMessage,
)
async def check_user_email(
    data_in: schemas.ICheckUserEmail,
) -> IResponseMessage:
    return await services.check_user_email(data_in)
