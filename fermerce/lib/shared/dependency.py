import typing as t
import uuid
import jose
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer

# from fermerce.app.users.permission.model import Permission
from fermerce.lib.errors import error
from fermerce.core.settings import config as base_config
from fermerce.lib.utils import get_api_prefix
from tortoise.models import Model


Oauth_schema = OAuth2PasswordBearer(
    tokenUrl=f"{get_api_prefix.get_prefix()}/auth/login"
)


class AppAuth:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    @staticmethod
    async def authenticate(
        token: str = Depends(Oauth_schema),
    ):
        try:
            payload: dict = jose.jwt.decode(
                token=token,
                key=base_config.secret_key,
                algorithms=[base_config.algorithm],
            )

            if not payload.get("user_id", None):
                raise AppAuth.credentials_exception
            return payload
        except jose.JWTError:
            raise AppAuth.credentials_exception

    @staticmethod
    async def verify_file_upload_api_key(
        api_key: str = Header(..., description="API key for file upload authorization")
    ):
        try:
            payload: dict = jose.jwt.decode(
                token=api_key,
                key=base_config.secret_key,
                algorithms=[base_config.algorithm],
            )

            if not payload.get("user_id", None):
                raise AppAuth.credentials_exception
            return payload
        except jose.JWTError:
            raise AppAuth.credentials_exception


ModelType = t.TypeVar("ModelType", bound=Model)


class AppWrite(t.Generic[ModelType]):
    def __init__(self, model: t.Type[ModelType]) -> None:
        self.model = model

    async def get_user_data(
        self,
        user_id: uuid.UUID,
    ) -> t.Union[ModelType, None]:
        if user_id:
            get_user = self.model.get_or_none(id=user_id)
            to_pre_fetch = set.union(
                self.model._meta.m2m_fields,
                self.model._meta.fk_fields,
                self.model._meta.o2o_fields,
                self.model._meta.backward_o2o_fields,
                self.model._meta.backward_fk_fields,
            )
            get_user = get_user.prefetch_related(*to_pre_fetch)
            get_user = await get_user
            print(get_user)
            if (
                get_user
                and get_user.is_verified
                and not get_user.is_archived
                and not get_user.is_suspended
            ):
                if get_user:
                    return get_user
                raise error.ForbiddenError("Authorization failed")
        return error.UnauthorizedError("Authorization failed")

    async def current_user(self, user_id: str = None):
        user: ModelType = await self.get_user_data(user_id=user_id)
        if user:
            return user
        raise error.UnauthorizedError("Authorization failed")
