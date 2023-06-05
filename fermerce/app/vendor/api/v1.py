import typing as t
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fermerce.app.vendor import schemas
from fermerce.app.vendor.models import Vendor
from fermerce.app.vendor.services import business
from fermerce.app.staff.dependency import require_super_admin
from fermerce.core.schemas.response import IResponseMessage
from fermerce.app.vendor import dependency
from fermerce.lib.errors import error
from fermerce.app.auth import schemas as auth_schemas
from fermerce.app.vendor.api import VENDOR_META

router = APIRouter(
    prefix=VENDOR_META.get("router_prefix"), tags=[VENDOR_META.get("tag")]
)
auth = APIRouter(
    prefix=f"{VENDOR_META.get('router_prefix')}/auth",
    tags=[VENDOR_META.get("tag")],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(data_in: schemas.IVendorIn, request: Request):
    return await business.create(data_in=data_in, request=request)


@router.put("/", status_code=status.HTTP_200_OK)
async def update_vendor_details(
    data_in: schemas.IVendorUpdateIn,
    request: Request,
    vendor=Depends(dependency.require_vendor),
):
    return await business.update(
        data_in=data_in,
        request=request,
        vendor=vendor,
    )


@router.get(
    "/whoami",
    status_code=status.HTTP_200_OK,
)
async def get_vendor_current_data(
    vendor: dict = Depends(dependency.AppAuth.authenticate),
    load_related: bool = False,
):
    if not vendor.get("user_id", None):
        raise error.UnauthorizedError()
    return await business.get_vendor_details(
        vendor.get("user_id", None), load_related=load_related
    )


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
    result = await business.login_vendor(
        data_in=data_in, request=request, task=task
    )
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
    return await business.refresh_login_token(
        data_in=data_in,
        request=request,
        task=task,
    )


@auth.post("/password/reset-link", status_code=status.HTTP_200_OK)
async def reset_password_link(
    vendor_data: schemas.IGetPasswordResetLink,
) -> IResponseMessage:
    return await business.reset_password_link(vendor_data)


@auth.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_vendor_email(
    data_in: schemas.IUserAccountVerifyToken,
) -> IResponseMessage:
    return await business.verify_vendor_email(data_in)


@auth.put("/password/reset", status_code=status.HTTP_200_OK)
async def update_vendor_password(
    data_in: schemas.IUserResetPassword,
) -> IResponseMessage:
    return await business.update_vendor_password(data_in)


@auth.put("/password/no_token", status_code=status.HTTP_200_OK)
async def update_vendor_password_no_token(
    data_in: schemas.IUserResetPasswordNoToken,
    vendor_data: Vendor = Depends(dependency.require_vendor),
) -> IResponseMessage:
    return await business.update_vendor_password_no_token(data_in, vendor_data)


@auth.post(
    "/check/dev",
    status_code=status.HTTP_200_OK,
    response_model=IResponseMessage,
)
async def check_user_email(
    data_in: schemas.ICheckUserEmail,
) -> IResponseMessage:
    return await business.check_user_email(data_in)


@router.get(
    "/{vendor_id}",
    response_model=t.Union[schemas.IVendorOutFull, schemas.IVendorOut],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_super_admin)],
)
async def get_vendor(
    vendor_id: uuid.UUID,
    load_related: bool = True,
):
    return await business.get_vendor_details(vendor_id, load_related)
