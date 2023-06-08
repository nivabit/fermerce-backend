from datetime import timedelta
import typing as t
import uuid
from fastapi import BackgroundTasks, Request, status
from fastapi import Response
from tortoise.expressions import Q
from fermerce.lib.utils import security
from fermerce.app.medias.models import Media
from fermerce.core.enum.sort_type import SortOrder
from fermerce.core.schemas.response import ITotalCount, IResponseMessage
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fermerce.core.enum.sort_type import SearchType
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.lib.errors import error
from fermerce.app.vendor import schemas, models
from fermerce.app.auth import services as auth_services, schemas as auth_schemas
from fermerce.taskiq.user import tasks


async def create(data_in=schemas.IVendorIn):
    check_business_name = await models.Vendor.get_or_none(
        business_name=data_in.business_name
    )
    if check_business_name:
        raise error.BadDataError("Business account already")
    to_create = dict(
        business_name=data_in.business_name,
        password=models.Vendor.generate_hash(
            data_in.password.get_secret_value(),
        ),
        phone_number=data_in.phone_number,
        email=data_in.email,
    )
    if data_in.logo:
        logo = await Media.get_or_none(id=data_in.logo)
        if logo:
            to_create.update({"logo": logo})
    new_vendor = await models.Vendor.create(**to_create)
    if new_vendor:
        await tasks.send_users_activation_email.kiq(
            dict(
                email=data_in.email,
                id=str(new_vendor.id),
                full_name=data_in.business_name,
            )
        )
        return IResponseMessage(
            message="Your email is not verified, Please check your for verification link before continuing"
        )
        return IResponseMessage(message="Vendor account was created successfully")
    raise error.ServerError("Error creating business account")


async def update(
    vendor: models.Vendor,
    data_in=schemas.IVendorUpdateIn,
):
    check_vendor = await models.Vendor.get_or_none(id=vendor.id)
    if not check_vendor:
        raise error.NotFoundError("Business Not found")
    check_business_name = await models.Vendor.get_or_none(
        business_name=data_in.business_name
    )
    if check_vendor.id != check_business_name.id:
        if check_business_name:
            raise error.BadDataError(
                f"Business with name {data_in.business_name} already exist"
            )
    to_update = dict(business_name=data_in.business_name)
    if data_in.logo:
        logo = await Media.get_or_none(id=data_in.logo)
        if logo:
            to_update.update({"logo": logo})
    check_vendor.update_from_dict(to_update)
    await check_vendor.save()
    return IResponseMessage(message="Vendor account was updated successfully")


async def login_vendor(
    request: Request,
    data_in: OAuth2PasswordRequestForm,
    task: BackgroundTasks,
) -> t.Union[auth_schemas.IToken, IResponseMessage]:
    check_vendor = await models.Vendor.get_or_none(email=data_in.username)
    if not check_vendor:
        raise error.UnauthorizedError(detail="incorrect email, username or password")
    if not check_vendor.check_password(data_in.password):
        raise error.UnauthorizedError(detail="incorrect email or password")
    if check_vendor.is_archived:
        raise error.UnauthorizedError()
    if check_vendor.is_suspended:
        raise error.UnauthorizedError("Your account is suspended")
    if not check_vendor.is_verified and check_vendor.is_active:
        await tasks.send_users_activation_email.kiq(
            dict(
                email=data_in.username,
                id=str(check_vendor.id),
                full_name=check_vendor.business_name,
            )
        )
        return IResponseMessage(
            message="Your email is not verified, Please check your for verification link before continuing"
        )
    token = await auth_services.login(
        request=request, task=task, user_id=check_vendor.id
    )
    if not token:
        raise error.ServerError("Count not authenticate vendor account")
    return token


async def check_business_name(
    data_in: schemas.ICheckUserEmail,
) -> IResponseMessage:
    check_user = await models.Vendor.get_or_none(
        Q(email=data_in.username) | Q(business_name=data_in.username)
    )
    if not check_user:
        raise error.NotFoundError()
    return IResponseMessage(message="Account exists")


async def refresh_login_token(
    data_in: auth_schemas.IRefreshToken, request: Request, task: BackgroundTasks
) -> auth_schemas.IToken:
    token = await auth_services.login_token_refresh(
        request=request, task=task, data_in=data_in
    )
    if not token:
        raise error.ServerError("Count not authenticate user")
    return token


async def verify_vendor_email(
    data_in: schemas.IUserAccountVerifyToken,
) -> IResponseMessage:
    data: dict = security.JWTAUTH.data_decoder(encoded_data=data_in.token)
    if not data.get("user_id", None):
        raise error.BadDataError("Invalid token data")
    vendor_obj = await models.Vendor.get_or_none(id=data.get("user_id", None))
    if not vendor_obj:
        raise error.BadDataError("Invalid token")

    if vendor_obj and vendor_obj.is_verified:
        raise error.BadDataError(
            detail="Account has been already verified",
        )
    vendor_obj = await models.Vendor.filter(id=vendor_obj.id).update(
        is_active=True, is_verified=True, is_suspended=False
    )
    if vendor_obj:
        return IResponseMessage(message="Account was verified successfully")
    raise error.ServerError("Could not activate account, please try again")


async def reset_password_link(
    data_in: schemas.IGetPasswordResetLink,
) -> IResponseMessage:
    vendor_obj = await models.Vendor.get_or_none(email=data_in.email)
    if not vendor_obj.is_verified:
        await tasks.send_users_activation_email.kiq(
            user=dict(
                email=vendor_obj.email,
                id=str(vendor_obj.id),
                full_name=vendor_obj.business_name,
            )
        )
        return IResponseMessage(
            message="account need to be verified, before reset their password"
        )
    if not vendor_obj:
        raise error.NotFoundError("Account not found")
    token = security.JWTAUTH.data_encoder(
        data={"user_id": str(vendor_obj.id)}, duration=timedelta(days=1)
    )
    await models.Vendor.filter(id=vendor_obj.id).update(reset_token=token)
    await tasks.send_users_password_reset_link.kiq(
        dict(
            email=vendor_obj.email,
            id=str(vendor_obj.id),
            token=token,
            full_name=vendor_obj.business_name,
        )
    )
    return IResponseMessage(
        message="Password reset token has been sent to your email, link expire after 24 hours"
    )


async def update_vendor_password(
    data_in: schemas.IUserResetPassword,
) -> IResponseMessage:
    token_data: dict = security.JWTAUTH.data_decoder(encoded_data=data_in.token)
    if token_data and token_data.get("user_id", None):
        vendor_obj = await models.Vendor.get_or_none(id=token_data.get("user_id", None))
        if not vendor_obj:
            raise error.NotFoundError("User not found")
        if vendor_obj.reset_token != data_in.token:
            raise error.UnauthorizedError()
        if vendor_obj.check_password(data_in.password.get_secret_value()):
            raise error.BadDataError("Try another password you have not used before")
        token = security.JWTAUTH.data_encoder(
            data={"user_id": str(vendor_obj.id)}, duration=timedelta(days=1)
        )
        if token:
            vendor_obj.update_from_dict(
                dict(
                    reset_token=None,
                    password=models.Vendor.generate_hash(
                        data_in.password.get_secret_value()
                    ),
                )
            )
            await tasks.send_verify_users_password_reset.kiq(
                dict(
                    email=vendor_obj.email,
                    token=token,
                    id=str(vendor_obj.id),
                    full_name=vendor_obj.business_name,
                )
            )
            await vendor_obj.save()
            return IResponseMessage(message="password was reset successfully")
    raise error.BadDataError("Invalid token was provided")


async def filter(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    load_related: bool = False,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
    is_active: bool = False,
    is_verified: bool = False,
    is_suspended: bool = False,
    is_archived: bool = False,
    search_type: SearchType = SearchType._and,
) -> t.List[models.Vendor]:
    query = models.Vendor
    if filter_string:
        query = query.filter(
            Q(business_name__icontains=filter_string)
            | Q(email__icontains=filter_string)
            | Q(phone_number__icontains=filter_string)
        )
    if search_type == SearchType._or:
        query = query.filter(
            Q(is_active=is_active)
            | Q(is_archived=is_archived)
            | Q(is_suspended=is_suspended)
            | Q(is_verified=is_verified)
        )
    else:
        query = query.filter(
            Q(is_active=is_active),
            Q(is_suspended=is_suspended),
            Q(is_archived=is_archived),
            Q(is_verified=is_verified),
        )

    return await filter_and_list(
        model=models.Vendor,
        query=query,
        page=page,
        load_related=load_related,
        per_page=per_page,
        select=select,
        sort_by=sort_by,
        order_by=order_by,
    )


async def update_vendor_password_no_token(
    data_in: schemas.IUserResetPasswordNoToken, vendor: models.Vendor
) -> IResponseMessage:
    if not vendor.check_password(data_in.old_password.get_secret_value()):
        raise error.BadDataError("Old password is incorrect")
    if vendor.check_password(data_in.password.get_secret_value()):
        raise error.BadDataError("Try another password you have not used before")
    vendor.update_from_dict(
        dict(
            password=models.Vendor.generate_hash(data_in.password.get_secret_value()),
            reset_token=None,
        )
    )
    await vendor.save()
    if vendor:
        await tasks.send_users_password_reset_link.kiq(
            dict(
                email=vendor.email,
                id=str(vendor.id),
                full_name=vendor.business_name,
            )
        )
        return IResponseMessage(message="password was reset successfully")
    raise error.BadDataError("Invalid token was provided")


async def remove_vendor_data(data_in: schemas.IRemoveVendor) -> None:
    vendor_to_remove = await models.Vendor.get_or_none(id=data_in.vendor_id)
    if vendor_to_remove:
        if data_in.permanent:
            await vendor_to_remove.delete()
        else:
            await vendor_to_remove.update_from_dict(
                dict(is_active=False, archived=True)
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise error.NotFoundError(
        f"Vendor with vendor_id {data_in.vendor_id} does not exist"
    )


async def get_vendor_details(vendor_id: uuid.UUID, load_related: bool = False):
    query = models.Vendor.filter(id=vendor_id)
    result = await filter_and_single(
        model=models.Vendor,
        query=query,
        load_related=load_related,
    )
    if result is not None:
        return result
    raise error.NotFoundError("Vendor not found")


async def get_total_Vendors():
    total_count = await models.Vendor.all().count()
    return ITotalCount(count=total_count)
