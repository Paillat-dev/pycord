from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel, Field, RootModel

from ..schemas import (
    ConnectedAccountResponse,
    MyGuildResponse,
    PrivateChannelResponse,
    PrivateGroupChannelResponse,
)


class UsersMeApplicationsApplicationIdRoleConnectionPutRequest(BaseModel):
    platform_name: Annotated[str | None, Field(max_length=50)] = None
    platform_username: Annotated[str | None, Field(max_length=100)] = None
    metadata: dict[str, Any] | None = None


class UsersMeChannelsPostResponse(
    RootModel[PrivateChannelResponse | PrivateGroupChannelResponse]
):
    root: PrivateChannelResponse | PrivateGroupChannelResponse


class UsersMeConnectionsGetResponse(RootModel[list[ConnectedAccountResponse]]):
    root: list[ConnectedAccountResponse]


class UsersMeGuildsGetResponse(RootModel[list[MyGuildResponse]]):
    root: list[MyGuildResponse]
