from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, RootModel

from ..schemas import SnowflakeType, StageInstancesPrivacyLevels


class StageInstancesChannelIdPatchRequest(BaseModel):
    topic: Annotated[str | None, Field(max_length=120, min_length=1)] = None
    privacy_level: StageInstancesPrivacyLevels | None = None


class StageInstancesPostRequest(BaseModel):
    topic: Annotated[str, Field(max_length=120, min_length=1)]
    channel_id: SnowflakeType
    privacy_level: StageInstancesPrivacyLevels | None = None
    guild_scheduled_event_id: SnowflakeType | None = None
    send_start_notification: bool | None = None
