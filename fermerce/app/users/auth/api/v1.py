import typing as t
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fermerce.app.users.auth.schemas import IRefreshToken, IToken
from fermerce.app.users.auth import services
from fermerce.core.schemas.response import IResponseMessage
from fastapi.security.oauth2 import OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/login",
    response_model=t.Union[IToken, IResponseMessage],
    status_code=status.HTTP_200_OK,
)
async def login(
    request: Request,
    task: BackgroundTasks,
    data_in: OAuth2PasswordRequestForm = Depends(),
) -> t.Union[IToken, IResponseMessage]:
    result = await services.login(data_in=data_in, request=request, task=task)

    return result


@router.post(
    "/token-refresh",
    response_model=IToken,
    status_code=status.HTTP_200_OK,
)
async def login_token_refresh(
    data_in: IRefreshToken,
    request: Request,
    task: BackgroundTasks,
):
    return await services.login_token_refresh(data_in=data_in, request=request, task=task)
