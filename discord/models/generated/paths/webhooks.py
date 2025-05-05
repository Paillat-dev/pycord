from __future__ import annotations

from typing import Annotated

from pydantic import AnyUrl, BaseModel, Field, RootModel

from ..schemas import (
    ApplicationIncomingWebhookResponse,
    ChannelFollowerWebhookResponse,
    GuildIncomingWebhookResponse,
    IncomingWebhookRequestPartial,
    IncomingWebhookUpdateRequestPartial,
    SnowflakeType,
)


class WebhooksWebhookIdGetResponse(
    RootModel[
        ApplicationIncomingWebhookResponse
        | ChannelFollowerWebhookResponse
        | GuildIncomingWebhookResponse
    ]
):
    root: (
        ApplicationIncomingWebhookResponse
        | ChannelFollowerWebhookResponse
        | GuildIncomingWebhookResponse
    )


class WebhooksWebhookIdPatchRequest(BaseModel):
    name: Annotated[str | None, Field(max_length=80, min_length=1)] = None
    avatar: str | None = None
    channel_id: SnowflakeType | None = None


class WebhooksWebhookIdPatchResponse(
    RootModel[
        ApplicationIncomingWebhookResponse
        | ChannelFollowerWebhookResponse
        | GuildIncomingWebhookResponse
    ]
):
    root: (
        ApplicationIncomingWebhookResponse
        | ChannelFollowerWebhookResponse
        | GuildIncomingWebhookResponse
    )


class WebhooksWebhookIdWebhookTokenGetResponse(
    RootModel[
        ApplicationIncomingWebhookResponse
        | ChannelFollowerWebhookResponse
        | GuildIncomingWebhookResponse
    ]
):
    root: (
        ApplicationIncomingWebhookResponse
        | ChannelFollowerWebhookResponse
        | GuildIncomingWebhookResponse
    )


class WebhooksWebhookIdWebhookTokenMessagesMessageIdPatchRequest(
    IncomingWebhookUpdateRequestPartial
):
    files_0_: Annotated[str | None, Field(alias="files[0]")] = None
    files_1_: Annotated[str | None, Field(alias="files[1]")] = None
    files_2_: Annotated[str | None, Field(alias="files[2]")] = None
    files_3_: Annotated[str | None, Field(alias="files[3]")] = None
    files_4_: Annotated[str | None, Field(alias="files[4]")] = None
    files_5_: Annotated[str | None, Field(alias="files[5]")] = None
    files_6_: Annotated[str | None, Field(alias="files[6]")] = None
    files_7_: Annotated[str | None, Field(alias="files[7]")] = None
    files_8_: Annotated[str | None, Field(alias="files[8]")] = None
    files_9_: Annotated[str | None, Field(alias="files[9]")] = None


class WebhooksWebhookIdWebhookTokenMessagesOriginalPatchRequest(
    IncomingWebhookUpdateRequestPartial
):
    files_0_: Annotated[str | None, Field(alias="files[0]")] = None
    files_1_: Annotated[str | None, Field(alias="files[1]")] = None
    files_2_: Annotated[str | None, Field(alias="files[2]")] = None
    files_3_: Annotated[str | None, Field(alias="files[3]")] = None
    files_4_: Annotated[str | None, Field(alias="files[4]")] = None
    files_5_: Annotated[str | None, Field(alias="files[5]")] = None
    files_6_: Annotated[str | None, Field(alias="files[6]")] = None
    files_7_: Annotated[str | None, Field(alias="files[7]")] = None
    files_8_: Annotated[str | None, Field(alias="files[8]")] = None
    files_9_: Annotated[str | None, Field(alias="files[9]")] = None


class WebhooksWebhookIdWebhookTokenPatchRequest(BaseModel):
    name: Annotated[str | None, Field(max_length=80, min_length=1)] = None
    avatar: str | None = None


class WebhooksWebhookIdWebhookTokenPatchResponse(
    RootModel[
        ApplicationIncomingWebhookResponse
        | ChannelFollowerWebhookResponse
        | GuildIncomingWebhookResponse
    ]
):
    root: (
        ApplicationIncomingWebhookResponse
        | ChannelFollowerWebhookResponse
        | GuildIncomingWebhookResponse
    )


class WebhooksWebhookIdWebhookTokenPostRequest(
    RootModel[IncomingWebhookRequestPartial | IncomingWebhookUpdateRequestPartial]
):
    root: IncomingWebhookRequestPartial | IncomingWebhookUpdateRequestPartial
