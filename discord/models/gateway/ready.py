from __future__ import annotations

from pydantic import BaseModel

from ..definitions import UserPII
from ..generated import GuildResponse, UserResponse
from ..type import MISSING, MissingSentinel, Snowflake
from .base import GatewayEvent


class UnavailableGuild(BaseModel):
    id: Snowflake
    unavailable: bool


class ReadyData(BaseModel):
    v: int
    user: UserPII
    private_channels: list[dict]  # TODO: Channel
    guilds: list[UnavailableGuild | GuildResponse]
    session_id: str
    shard: list[int] | MissingSentinel = MISSING
    application: dict  # TODO: Application

    # @field_validator("guilds", mode='plain')
    # def guilds_validator(cls, guilds: list[dict[str, Any]]) -> list[Guild | UnavailableGuild]:  # pyright: ignore [reportExplicitAny]
    #    r: list[Guild | UnavailableGuild] = []
    #    for guild in guilds:
    #        if guild.get("unavailable", False):
    #            r.append(UnavailableGuild(**guild))
    #        else:
    #            r.append(Guild(**guild))
    #    return r


class Ready(GatewayEvent[ReadyData]):
    pass
