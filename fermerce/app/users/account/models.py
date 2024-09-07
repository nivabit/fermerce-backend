from typing import Any
from edgy import fields
from fermerce.core.model.base_model import BaseModel
from fermerce.lib.utils.password_hasher import Hasher


import edgy

from esmerald.contrib.auth.hashers import (
    check_password,
    is_password_usable,
    make_password,
)


class AbstractUser(edgy.Model):
    username = fields.CharField(max_length=20, unique=True, index=True)
    firstname = fields.CharField(max_length=50, null=True, index=True)
    lastname = fields.CharField(max_length=50, null=True, unique=True, index=True)
    email = fields.CharField(max_length=70, null=False, unique=True, index=True)
    password = fields.PasswordField(max_length=255, null=True, secret=True)
    is_verified = fields.BooleanField(default=False, null=True)
    is_suspended = fields.BooleanField(default=False, null=True)
    is_active = fields.BooleanField(default=False, null=True)
    is_archived = fields.BooleanField(default=False, null=True)
    reset_token = fields.CharField(max_length=255, null=True, secret=True)
    created_at = fields.DateTimeField(auto_now_add=True)
    modified_at = fields.DateTimeField(auto_now=True)

    _password = None

    class Meta:
        abstract = True

    @property
    async def is_authenticated(self) -> bool:
        """
        Always return True.
        """
        return True

    @property
    def can_login(self) -> bool:
        """
        return self.is_active and not self.is_suspended and self.is_verified
        """
        return self.is_active and not self.is_suspended and self.is_verified

    async def set_password(self, raw_password: str) -> None:
        self.password = make_password(raw_password)
        self._password = raw_password
        await self.update(password=make_password(raw_password))

    async def check_password(self, raw_password: str) -> bool:
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        async def setter(raw_password: str) -> None:
            await self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            await self.update(password=self.password)

        return await check_password(raw_password, str(self.password), setter)

    async def set_unusable_password(self) -> None:
        # Set a value that will never be a valid hash
        self.password = make_password(None)

    async def has_usable_password(self) -> bool:
        """
        Return False if set_unusable_password() has been called for this user.
        """
        return is_password_usable(self.password)

    @classmethod
    async def _create_user(
        cls, username: str, email: str, password: str, **extra_fields: Any
    ) -> "AbstractUser":
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")
        password = make_password(password)
        user: AbstractUser = await cls.query.create(
            username=username, email=email, password=password, **extra_fields
        )
        return user

    @classmethod
    async def create_user(
        cls,
        username: str,
        email: str,
        password: str,
        **extra_fields: Any,
    ) -> "AbstractUser":
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return await cls._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Implementation of the Abstract user and can be used directly.
    """

    shipping_address = fields.ManyToManyField(
        "Address",
        through="fm_shipping_address",
        related_name="users",
    )

    ...
