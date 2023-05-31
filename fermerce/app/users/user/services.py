from datetime import timedelta
import typing as t
import uuid
from fastapi import BackgroundTasks, Request, status
from fastapi import Response
from tortoise.expressions import Q
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fermerce.core.enum.sort_type import SortOrder, SearchType
from fermerce.core.schemas.response import ITotalCount, IResponseMessage
from fermerce.core.services.base import filter_and_list, filter_and_single
from fermerce.taskiq.user import tasks
from fermerce.lib.errors import error
from fermerce.app.users.user import schemas, models
from fermerce.lib.utils import security
from fermerce.app.users.auth import services as auth_services, schemas as auth_schemas


async def create(data_in=schemas.IUserIn):
    check_user = await models.User.get_or_none(
        Q(email=data_in.email) | Q(username=data_in.username)
    )
    if check_user:
        raise error.DuplicateError("Account already exist")
    new_user = await models.User.create(
        **data_in.dict(exclude={"password"}),
        password=models.User.generate_hash(data_in.password.get_secret_value()),
    )
    full_name = None
    if new_user.firstname and new_user.lastname:
        full_name = f"{new_user.firstname} {new_user.lastname}"
    else:
        full_name = new_user.username

    if new_user:
        await tasks.send_users_activation_email.kiq(
            dict(email=new_user.email, id=str(new_user.id), full_name=full_name)
        )

        return IResponseMessage(
            message="Account was created successfully, check your email to activate your account"
        )
    raise error.ServerError("Could not create account, please try again")


async def update_user_details(data_in=schemas.IUserUpdateIn):
    check_user = await models.User.get_or_none(id=data_in.id)
    if not check_user:
        raise error.NotFoundError("Account does not exist")
    if data_in.email and check_user.email != data_in.email:
        check_existing_email = await models.User.get_or_none(
            Q(email=check_user.email)
            if data_in.email
            else None | Q(username=data_in.username)
            if data_in.email
            else None
        )
        if str(check_existing_email.id) != check_user.id:
            raise error.BadDataError("Account with this details already exists")
    users_update = check_user.update_from_dict(
        data_in.dict(exclude={"id"}, exclude_unset=True),
    )
    await users_update.save()

    if not users_update:
        raise error.ServerError("Could not updating  details, please try again")

    if users_update and data_in.email:
        await tasks.send_email_verification_email.kiq(
            dict(
                email=users_update.email,
                id=str(users_update.id),
                full_name=f"{users_update.firstname} {users_update.lastname}"
                if users_update.firstname and users_update.lastname
                else users_update.username,
            )
        )
        return IResponseMessage(
            message="Account was updated successfully, please check your email to confirm your email shipping_address"
        )
    else:
        return IResponseMessage(
            message="Account was updated successfully, please check your email to activate your account"
        )


async def login(
    request: Request,
    data_in: OAuth2PasswordRequestForm,
    task: BackgroundTasks,
) -> t.Union[auth_schemas.IToken, IResponseMessage]:
    check_user = await models.User.get_or_none(
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
    token = await auth_services.login(request=request, task=task, user_id=check_user.id)
    if not token:
        raise error.ServerError("Count not authenticate user")
    return token


async def refresh_login_token(
    data_in: auth_schemas.IRefreshToken, request: Request, task: BackgroundTasks
) -> auth_schemas.IToken:
    token = await auth_services.login_token_refresh(
        request=request, task=task, data_in=data_in
    )
    if not token:
        raise error.ServerError("Count not authenticate user")
    return token


# # get all permissions
async def filter(
    filter_string: str,
    per_page: int = 10,
    page: int = 0,
    select: str = "",
    load_related: bool = False,
    sort_by: SortOrder = SortOrder.asc,
    order_by: str = None,
    is_active: bool = False,
    is_suspended: bool = False,
    is_archived: bool = False,
    search_type: SearchType = SearchType._and,
) -> t.List[models.User]:
    query = None
    if search_type == SearchType._or:
        query = models.User.filter(
            Q(is_active=is_active)
            | Q(is_archived=is_archived)
            | Q(is_suspended=is_suspended)
        )
    else:
        query = models.User.filter(
            Q(is_active=is_active),
            Q(is_suspended=is_suspended),
            Q(is_archived=is_archived),
            Q(is_suspended=is_suspended),
        )
    if filter_string:
        query = query.filter(
            Q(firstname__icontains=filter_string)
            | Q(lastname__icontains=filter_string)
            | Q(email__icontains=filter_string)
            | Q(username__icontains=filter_string)
        )
    result = await filter_and_list(
        model=models.User,
        query=query,
        page=page,
        load_related=load_related,
        per_page=per_page,
        select=select,
        sort_by=sort_by,
        order_by=order_by,
    )
    return result


async def verify_users_email(
    data_in: schemas.IUserAccountVerifyToken,
) -> IResponseMessage:
    data: dict = security.JWTAUTH.data_decoder(encoded_data=data_in.token)
    if not data.get("user_id", None):
        raise error.BadDataError("Invalid token data")
    users_obj = await models.User.get_or_none(id=data.get("user_id", None))
    if not users_obj:
        raise error.BadDataError("Invalid token")

    if users_obj and users_obj.is_verified:
        raise error.BadDataError(
            detail="Account has been already verified",
        )
    users_obj = await models.User.filter(id=users_obj.id).update(
        is_active=True, is_verified=True, is_suspended=False
    )
    if users_obj:
        return IResponseMessage(message="Account was verified successfully")
    raise error.ServerError("Could not activate account, please try again")


async def reset_password_link(
    data_in: schemas.IGetPasswordResetLink,
) -> IResponseMessage:
    users_obj = await models.User.get_or_none(email=data_in.email)
    if not users_obj.is_verified:
        await tasks.send_users_activation_email.kiq(
            user=dict(
                email=users_obj.email,
                id=str(users_obj.id),
                full_name=f"{users_obj.firstname} {users_obj.lastname}"
                if users_obj.firstname and users_obj.lastname
                else users_obj.username,
            )
        )
        return IResponseMessage(
            message="account need to be verified, before reset their password"
        )
    if not users_obj:
        raise error.NotFoundError("User not found")
    token = security.JWTAUTH.data_encoder(
        data={"user_id": str(users_obj.id)}, duration=timedelta(days=1)
    )
    await models.User.filter(id=users_obj.id).update(reset_token=token)
    await tasks.send_users_password_reset_link.kiq(
        dict(
            email=users_obj.email,
            id=str(users_obj.id),
            token=token,
            full_name=f"{users_obj.firstname} {users_obj.lastname}"
            if users_obj.firstname and users_obj.lastname
            else users_obj.username,
        )
    )
    return IResponseMessage(
        message="Password reset token has been sent to your email, link expire after 24 hours"
    )


async def update_user_password(
    data_in: schemas.IUserResetPassword,
) -> IResponseMessage:
    token_data: dict = security.JWTAUTH.data_decoder(encoded_data=data_in.token)
    if token_data and token_data.get("user_id", None):
        users_obj = await models.User.get_or_none(id=token_data.get("user_id", None))
        if not users_obj:
            raise error.NotFoundError("User not found")
        if users_obj.reset_token != data_in.token:
            raise error.UnauthorizedError()
        if users_obj.check_password(data_in.password.get_secret_value()):
            raise error.BadDataError("Try another password you have not used before")
        token = security.JWTAUTH.data_encoder(
            data={"user_id": str(users_obj.id)}, duration=timedelta(days=1)
        )
        if token:
            await models.User.filter(id=users_obj.id).update(
                reset_token=token,
                password=models.User.generate_hash(data_in.password.get_secret_value()),
            )
            await tasks.send_verify_users_password_reset.kiq(
                dict(
                    email=users_obj.email,
                    token=token,
                    id=str(users_obj.id),
                    full_name=f"{users_obj.firstname} {users_obj.lastname}"
                    if users_obj.firstname and users_obj.lastname
                    else users_obj.username,
                )
            )
            return IResponseMessage(message="password was reset successfully")
    raise error.BadDataError("Invalid token was provided")


async def update_users_password_no_token(
    data_in: schemas.IUserResetPasswordNoToken, user_obj: models.User
) -> IResponseMessage:
    if not user_obj:
        raise error.NotFoundError("User not found")
    if not user_obj.check_password(data_in.old_password.get_secret_value()):
        raise error.BadDataError("Old password is incorrect")

    if user_obj.check_password(data_in.password.get_secret_value()):
        raise error.BadDataError("Try another password you have not used before")
    if await user_obj.update_from_dict(
        password=models.User.generate_hash(data_in.password.get_secret_value())
    ):
        await tasks.send_users_password_reset_link.kiq(
            dict(
                email=user_obj.email,
                id=str(user_obj.id),
                full_name=f"{user_obj.firstname} {user_obj.lastname}",
            )
        )
        return IResponseMessage(message="password was reset successfully")
    raise error.BadDataError("Invalid token was provided")


async def remove_users_data(data_in: schemas.IUserRemove) -> None:
    user_to_remove = await models.User.get_or_none(id=data_in.user_id)
    if user_to_remove:
        if data_in.permanent:
            await models.User.filter(id=user_to_remove.id).delete()
        else:
            await models.User.filter(id=user_to_remove.id).update(is_archived=True)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise error.NotFoundError(f"User with  user id {data_in.user_id} does not exist")


async def get_total_users():
    total_count = await models.User.all().count()
    return ITotalCount(count=total_count).dict()


async def get_user(user_id: uuid.UUID, load_related: bool = False) -> models.User:
    query = models.User.filter(id=user_id)
    try:
        result = await filter_and_single(
            model=models.User, query=query, load_related=load_related
        )
        if not result:
            raise error.NotFoundError("No user with the provided credential")
        if load_related:
            # return schemas.IUserFullOut(**result)
            return result
        return result
    except Exception as e:
        raise error.ServerError(f"Error getting user data {e}")


async def check_user_email(
    data_in: schemas.ICheckUserEmail,
) -> IResponseMessage:
    check_user = await models.User.get_or_none(
        Q(email=data_in.username) | Q(username=data_in.username)
    )
    if not check_user:
        raise error.NotFoundError()
    return IResponseMessage(message="Account exists")
