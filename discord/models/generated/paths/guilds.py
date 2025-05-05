from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import AnyUrl, BaseModel, Field, RootModel

from ..schemas import (
    ApplicationIncomingWebhookResponse,
    ChannelFollowerWebhookResponse,
    DefaultKeywordListUpsertRequest,
    DefaultKeywordListUpsertRequestPartial,
    DefaultKeywordRuleResponse,
    DiscordIntegrationResponse,
    EmojiResponse,
    ExternalConnectionIntegrationResponse,
    ExternalScheduledEventCreateRequest,
    ExternalScheduledEventPatchRequestPartial,
    ExternalScheduledEventResponse,
    FriendInviteResponse,
    GroupDMInviteResponse,
    GuildBanResponse,
    GuildChannelResponse,
    GuildIncomingWebhookResponse,
    GuildInviteResponse,
    GuildMemberResponse,
    GuildMFALevel,
    GuildRoleResponse,
    GuildStickerResponse,
    GuildSubscriptionIntegrationResponse,
    GuildTemplateResponse,
    KeywordRuleResponse,
    KeywordUpsertRequest,
    KeywordUpsertRequestPartial,
    MentionSpamRuleResponse,
    MentionSpamUpsertRequest,
    MentionSpamUpsertRequestPartial,
    MLSpamRuleResponse,
    MLSpamUpsertRequest,
    MLSpamUpsertRequestPartial,
    PrivateChannelResponse,
    PrivateGroupChannelResponse,
    ScheduledEventUserResponse,
    SnowflakeType,
    SpamLinkRuleResponse,
    StageScheduledEventCreateRequest,
    StageScheduledEventPatchRequestPartial,
    StageScheduledEventResponse,
    ThreadResponse,
    VoiceRegionResponse,
    VoiceScheduledEventCreateRequest,
    VoiceScheduledEventPatchRequestPartial,
    VoiceScheduledEventResponse,
)


class GuildsGuildIdAutoModerationRulesGetResponse(
    RootModel[
        list[
            DefaultKeywordRuleResponse
            | KeywordRuleResponse
            | MLSpamRuleResponse
            | MentionSpamRuleResponse
            | SpamLinkRuleResponse
            | None
        ]
    ]
):
    root: list[
        DefaultKeywordRuleResponse
        | KeywordRuleResponse
        | MLSpamRuleResponse
        | MentionSpamRuleResponse
        | SpamLinkRuleResponse
        | None
    ]


class GuildsGuildIdAutoModerationRulesPostRequest(
    RootModel[
        DefaultKeywordListUpsertRequest
        | KeywordUpsertRequest
        | MLSpamUpsertRequest
        | MentionSpamUpsertRequest
    ]
):
    root: (
        DefaultKeywordListUpsertRequest
        | KeywordUpsertRequest
        | MLSpamUpsertRequest
        | MentionSpamUpsertRequest
    )


class GuildsGuildIdAutoModerationRulesPostResponse(
    RootModel[
        DefaultKeywordRuleResponse
        | KeywordRuleResponse
        | MLSpamRuleResponse
        | MentionSpamRuleResponse
        | SpamLinkRuleResponse
    ]
):
    root: (
        DefaultKeywordRuleResponse
        | KeywordRuleResponse
        | MLSpamRuleResponse
        | MentionSpamRuleResponse
        | SpamLinkRuleResponse
    )


class GuildsGuildIdAutoModerationRulesRuleIdGetResponse(
    RootModel[
        DefaultKeywordRuleResponse
        | KeywordRuleResponse
        | MLSpamRuleResponse
        | MentionSpamRuleResponse
        | SpamLinkRuleResponse
    ]
):
    root: (
        DefaultKeywordRuleResponse
        | KeywordRuleResponse
        | MLSpamRuleResponse
        | MentionSpamRuleResponse
        | SpamLinkRuleResponse
    )


class GuildsGuildIdAutoModerationRulesRuleIdPatchRequest(
    RootModel[
        DefaultKeywordListUpsertRequestPartial
        | KeywordUpsertRequestPartial
        | MLSpamUpsertRequestPartial
        | MentionSpamUpsertRequestPartial
    ]
):
    root: (
        DefaultKeywordListUpsertRequestPartial
        | KeywordUpsertRequestPartial
        | MLSpamUpsertRequestPartial
        | MentionSpamUpsertRequestPartial
    )


class GuildsGuildIdAutoModerationRulesRuleIdPatchResponse(
    RootModel[
        DefaultKeywordRuleResponse
        | KeywordRuleResponse
        | MLSpamRuleResponse
        | MentionSpamRuleResponse
        | SpamLinkRuleResponse
    ]
):
    root: (
        DefaultKeywordRuleResponse
        | KeywordRuleResponse
        | MLSpamRuleResponse
        | MentionSpamRuleResponse
        | SpamLinkRuleResponse
    )


class GuildsGuildIdBansGetResponse(RootModel[list[GuildBanResponse]]):
    root: list[GuildBanResponse]


class GuildsGuildIdBansUserIdPutRequest(BaseModel):
    delete_message_seconds: Annotated[int | None, Field(ge=0, le=604800)] = None
    delete_message_days: Annotated[int | None, Field(ge=0, le=7)] = None


class GuildsGuildIdBulkBanPostRequest(BaseModel):
    user_ids: Annotated[list[SnowflakeType], Field(max_length=200)]
    delete_message_seconds: Annotated[int | None, Field(ge=0, le=604800)] = None


class GuildsGuildIdChannelsGetResponse(
    RootModel[
        list[
            GuildChannelResponse
            | PrivateChannelResponse
            | PrivateGroupChannelResponse
            | ThreadResponse
        ]
    ]
):
    root: list[
        GuildChannelResponse
        | PrivateChannelResponse
        | PrivateGroupChannelResponse
        | ThreadResponse
    ]


class GuildsGuildIdChannelsPatchRequest(
    RootModel["list[GuildsGuildIdChannelsPatchRequestItem]"]
):
    root: list[GuildsGuildIdChannelsPatchRequestItem]


class GuildsGuildIdChannelsPatchRequestItem(BaseModel):
    id: SnowflakeType | None = None
    position: Annotated[int | None, Field(ge=0)] = None
    parent_id: SnowflakeType | None = None
    lock_permissions: bool | None = None


class GuildsGuildIdEmojisEmojiIdPatchRequest(BaseModel):
    name: Annotated[str | None, Field(max_length=32, min_length=2)] = None
    roles: Annotated[list[SnowflakeType | None] | None, Field(max_length=1521)] = None


class GuildsGuildIdEmojisGetResponse(RootModel[list[EmojiResponse]]):
    root: list[EmojiResponse]


class GuildsGuildIdEmojisPostRequest(BaseModel):
    name: Annotated[str, Field(max_length=32, min_length=2)]
    image: str
    roles: Annotated[list[SnowflakeType | None] | None, Field(max_length=1521)] = None


class GuildsGuildIdIntegrationsGetResponse(
    RootModel[
        list[
            DiscordIntegrationResponse
            | ExternalConnectionIntegrationResponse
            | GuildSubscriptionIntegrationResponse
        ]
    ]
):
    root: list[
        DiscordIntegrationResponse
        | ExternalConnectionIntegrationResponse
        | GuildSubscriptionIntegrationResponse
    ]


class GuildsGuildIdInvitesGetResponse(
    RootModel[list[FriendInviteResponse | GroupDMInviteResponse | GuildInviteResponse]]
):
    root: list[FriendInviteResponse | GroupDMInviteResponse | GuildInviteResponse]


class GuildsGuildIdMembersGetResponse(RootModel[list[GuildMemberResponse]]):
    root: list[GuildMemberResponse]


class GuildsGuildIdMembersMePatchRequest(BaseModel):
    nick: Annotated[str | None, Field(max_length=32)] = None


class GuildsGuildIdMembersSearchGetResponse(RootModel[list[GuildMemberResponse]]):
    root: list[GuildMemberResponse]


class GuildsGuildIdMembersUserIdPatchRequest(BaseModel):
    nick: Annotated[str | None, Field(max_length=32)] = None
    roles: Annotated[list[SnowflakeType | None] | None, Field(max_length=1521)] = None
    mute: bool | None = None
    deaf: bool | None = None
    channel_id: SnowflakeType | None = None
    communication_disabled_until: datetime | None = None
    flags: int | None = None


class GuildsGuildIdMembersUserIdPutRequest(BaseModel):
    nick: Annotated[str | None, Field(max_length=32)] = None
    roles: Annotated[list[SnowflakeType | None] | None, Field(max_length=1521)] = None
    mute: bool | None = None
    deaf: bool | None = None
    access_token: Annotated[str, Field(max_length=152133)]
    flags: int | None = None


class GuildsGuildIdMfaPostRequest(BaseModel):
    level: GuildMFALevel


class GuildsGuildIdPrunePostRequest(BaseModel):
    days: Annotated[int | None, Field(ge=1, le=30)] = None
    compute_prune_count: bool | None = None
    include_roles: str | IncludeRoles | None = None


class GuildsGuildIdRegionsGetResponse(RootModel[list[VoiceRegionResponse]]):
    root: list[VoiceRegionResponse]


class GuildsGuildIdRolesGetResponse(RootModel[list[GuildRoleResponse]]):
    root: list[GuildRoleResponse]


class GuildsGuildIdRolesPatchRequest(
    RootModel["list[GuildsGuildIdRolesPatchRequestItem]"]
):
    root: list[GuildsGuildIdRolesPatchRequestItem]


class GuildsGuildIdRolesPatchRequestItem(BaseModel):
    id: SnowflakeType | None = None
    position: int | None = None


class GuildsGuildIdRolesPatchResponse(RootModel[list[GuildRoleResponse]]):
    root: list[GuildRoleResponse]


class GuildsGuildIdRolesPostRequest(BaseModel):
    name: Annotated[str | None, Field(max_length=100)] = None
    permissions: int | None = None
    color: Annotated[int | None, Field(ge=0, le=16777215)] = None
    hoist: bool | None = None
    mentionable: bool | None = None
    icon: str | None = None
    unicode_emoji: Annotated[str | None, Field(max_length=100)] = None


class GuildsGuildIdRolesRoleIdPatchRequest(BaseModel):
    name: Annotated[str | None, Field(max_length=100)] = None
    permissions: int | None = None
    color: Annotated[int | None, Field(ge=0, le=16777215)] = None
    hoist: bool | None = None
    mentionable: bool | None = None
    icon: str | None = None
    unicode_emoji: Annotated[str | None, Field(max_length=100)] = None


class GuildsGuildIdScheduledEventsGetResponse(
    RootModel[
        list[
            ExternalScheduledEventResponse
            | StageScheduledEventResponse
            | VoiceScheduledEventResponse
        ]
    ]
):
    root: list[
        ExternalScheduledEventResponse
        | StageScheduledEventResponse
        | VoiceScheduledEventResponse
    ]


class GuildsGuildIdScheduledEventsGuildScheduledEventIdGetResponse(
    RootModel[
        ExternalScheduledEventResponse
        | StageScheduledEventResponse
        | VoiceScheduledEventResponse
    ]
):
    root: (
        ExternalScheduledEventResponse
        | StageScheduledEventResponse
        | VoiceScheduledEventResponse
    )


class GuildsGuildIdScheduledEventsGuildScheduledEventIdPatchRequest(
    RootModel[
        ExternalScheduledEventPatchRequestPartial
        | StageScheduledEventPatchRequestPartial
        | VoiceScheduledEventPatchRequestPartial
    ]
):
    root: (
        ExternalScheduledEventPatchRequestPartial
        | StageScheduledEventPatchRequestPartial
        | VoiceScheduledEventPatchRequestPartial
    )


class GuildsGuildIdScheduledEventsGuildScheduledEventIdPatchResponse(
    RootModel[
        ExternalScheduledEventResponse
        | StageScheduledEventResponse
        | VoiceScheduledEventResponse
    ]
):
    root: (
        ExternalScheduledEventResponse
        | StageScheduledEventResponse
        | VoiceScheduledEventResponse
    )


class GuildsGuildIdScheduledEventsGuildScheduledEventIdUsersGetResponse(
    RootModel[list[ScheduledEventUserResponse]]
):
    root: list[ScheduledEventUserResponse]


class GuildsGuildIdScheduledEventsPostRequest(
    RootModel[
        ExternalScheduledEventCreateRequest
        | StageScheduledEventCreateRequest
        | VoiceScheduledEventCreateRequest
    ]
):
    root: (
        ExternalScheduledEventCreateRequest
        | StageScheduledEventCreateRequest
        | VoiceScheduledEventCreateRequest
    )


class GuildsGuildIdScheduledEventsPostResponse(
    RootModel[
        ExternalScheduledEventResponse
        | StageScheduledEventResponse
        | VoiceScheduledEventResponse
    ]
):
    root: (
        ExternalScheduledEventResponse
        | StageScheduledEventResponse
        | VoiceScheduledEventResponse
    )


class GuildsGuildIdStickersGetResponse(RootModel[list[GuildStickerResponse]]):
    root: list[GuildStickerResponse]


class GuildsGuildIdStickersPostRequest(BaseModel):
    name: Annotated[str, Field(max_length=30, min_length=2)]
    tags: Annotated[str, Field(max_length=200, min_length=1)]
    description: Annotated[str | None, Field(max_length=100)] = None
    file: str


class GuildsGuildIdStickersStickerIdPatchRequest(BaseModel):
    name: Annotated[str | None, Field(max_length=30, min_length=2)] = None
    tags: Annotated[str | None, Field(max_length=200, min_length=1)] = None
    description: Annotated[str | None, Field(max_length=100)] = None


class GuildsGuildIdTemplatesCodePatchRequest(BaseModel):
    name: Annotated[str | None, Field(max_length=100, min_length=1)] = None
    description: Annotated[str | None, Field(max_length=120)] = None


class GuildsGuildIdTemplatesGetResponse(RootModel[list[GuildTemplateResponse]]):
    root: list[GuildTemplateResponse]


class GuildsGuildIdTemplatesPostRequest(BaseModel):
    name: Annotated[str, Field(max_length=100, min_length=1)]
    description: Annotated[str | None, Field(max_length=120)] = None


class GuildsGuildIdVoiceStatesMePatchRequest(BaseModel):
    request_to_speak_timestamp: datetime | None = None
    suppress: bool | None = None
    channel_id: SnowflakeType | None = None


class GuildsGuildIdVoiceStatesUserIdPatchRequest(BaseModel):
    suppress: bool | None = None
    channel_id: SnowflakeType | None = None


class GuildsGuildIdWebhooksGetResponse(
    RootModel[
        list[
            ApplicationIncomingWebhookResponse
            | ChannelFollowerWebhookResponse
            | GuildIncomingWebhookResponse
        ]
    ]
):
    root: list[
        ApplicationIncomingWebhookResponse
        | ChannelFollowerWebhookResponse
        | GuildIncomingWebhookResponse
    ]


class GuildsGuildIdWidgetPatchRequest(BaseModel):
    channel_id: SnowflakeType | None = None
    enabled: bool | None = None


class GuildsTemplatesCodePostRequest(BaseModel):
    name: Annotated[str, Field(max_length=100, min_length=2)]
    icon: str | None = None


class IncludeRoles(RootModel[list[SnowflakeType | None]]):
    root: Annotated[list[SnowflakeType | None], Field(max_length=100)]
