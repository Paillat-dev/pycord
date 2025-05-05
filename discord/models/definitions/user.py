from ..flags import UserFlags
from ..generated import (
    UserPrimaryGuildResponse,  # pyright: ignore [reportUnusedImport] # needs to be imported for pydantic
)
from ..generated import UserPIIResponse, UserResponse


class UserMixin:
    flags: UserFlags | None = None
    public_flags: UserFlags | None = None


class User(UserMixin, UserResponse):
    pass


class UserPII(UserMixin, UserPIIResponse):
    pass


__all__ = ("User", "UserPII")
