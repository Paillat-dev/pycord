from __future__ import annotations

from typing import Annotated

from pydantic import AnyUrl, BaseModel, Field, RootModel

from ..schemas import (
    ApplicationIncomingWebhookResponse,
    ChannelFollowerWebhookResponse,
    ChannelPermissionOverwrites,
    CreateForumThreadRequest,
    CreateGroupDMInviteRequest,
    CreateGuildInviteRequest,
    CreateTextThreadWithoutMessageRequest,
    FriendInviteResponse,
    GroupDMInviteResponse,
    GuildChannelResponse,
    GuildIncomingWebhookResponse,
    GuildInviteResponse,
    MessageCreateRequest,
    MessageEditRequestPartial,
    MessageResponse,
    PrivateChannelResponse,
    PrivateGroupChannelResponse,
    SnowflakeType,
    ThreadMemberResponse,
    ThreadResponse,
    UpdateDMRequestPartial,
    UpdateGroupDMRequestPartial,
    UpdateGuildChannelRequestPartial,
    UpdateThreadRequestPartial,
    UserResponse,
)


class ChannelsChannelIdDeleteResponse(
    RootModel[
        GuildChannelResponse
        | PrivateChannelResponse
        | PrivateGroupChannelResponse
        | ThreadResponse
    ]
):
    root: (
        GuildChannelResponse
        | PrivateChannelResponse
        | PrivateGroupChannelResponse
        | ThreadResponse
    )


class ChannelsChannelIdFollowersPostRequest(BaseModel):
    webhook_channel_id: SnowflakeType


class ChannelsChannelIdGetResponse(
    RootModel[
        GuildChannelResponse
        | PrivateChannelResponse
        | PrivateGroupChannelResponse
        | ThreadResponse
    ]
):
    root: (
        GuildChannelResponse
        | PrivateChannelResponse
        | PrivateGroupChannelResponse
        | ThreadResponse
    )


class ChannelsChannelIdInvitesGetResponse(
    RootModel[list[FriendInviteResponse | GroupDMInviteResponse | GuildInviteResponse]]
):
    root: list[FriendInviteResponse | GroupDMInviteResponse | GuildInviteResponse]


class ChannelsChannelIdInvitesPostRequest(
    RootModel[CreateGroupDMInviteRequest | CreateGuildInviteRequest]
):
    root: CreateGroupDMInviteRequest | CreateGuildInviteRequest


class ChannelsChannelIdInvitesPostResponse(
    RootModel[FriendInviteResponse | GroupDMInviteResponse | GuildInviteResponse]
):
    root: FriendInviteResponse | GroupDMInviteResponse | GuildInviteResponse


class ChannelsChannelIdMessagesBulkDeletePostRequest(BaseModel):
    messages: Annotated[list[SnowflakeType], Field(max_length=100, min_length=2)]


class ChannelsChannelIdMessagesGetResponse(RootModel[list[MessageResponse]]):
    root: list[MessageResponse]


class ChannelsChannelIdMessagesMessageIdReactionsEmojiNameGetResponse(
    RootModel[list[UserResponse]]
):
    root: list[UserResponse]


class ChannelsChannelIdPatchRequest(
    RootModel[
        UpdateDMRequestPartial
        | UpdateGroupDMRequestPartial
        | UpdateGuildChannelRequestPartial
        | UpdateThreadRequestPartial
    ]
):
    root: (
        UpdateDMRequestPartial
        | UpdateGroupDMRequestPartial
        | UpdateGuildChannelRequestPartial
        | UpdateThreadRequestPartial
    )


class ChannelsChannelIdPatchResponse(
    RootModel[
        GuildChannelResponse
        | PrivateChannelResponse
        | PrivateGroupChannelResponse
        | ThreadResponse
    ]
):
    root: (
        GuildChannelResponse
        | PrivateChannelResponse
        | PrivateGroupChannelResponse
        | ThreadResponse
    )


class ChannelsChannelIdPermissionsOverwriteIdPutRequest(BaseModel):
    type: ChannelPermissionOverwrites | None = None
    allow: int | None = None
    deny: int | None = None


class ChannelsChannelIdPinsGetResponse(RootModel[list[MessageResponse]]):
    root: list[MessageResponse]


class ChannelsChannelIdRecipientsUserIdPutRequest(BaseModel):
    access_token: Annotated[str | None, Field(max_length=152133)] = None
    nick: Annotated[str | None, Field(max_length=152133)] = None


class ChannelsChannelIdRecipientsUserIdPutResponse(
    RootModel[PrivateChannelResponse | PrivateGroupChannelResponse]
):
    root: PrivateChannelResponse | PrivateGroupChannelResponse


class ChannelsChannelIdThreadMembersGetResponse(RootModel[list[ThreadMemberResponse]]):
    root: list[ThreadMemberResponse]


class ChannelsChannelIdThreadsPostRequest(
    RootModel[CreateForumThreadRequest | CreateTextThreadWithoutMessageRequest]
):
    root: CreateForumThreadRequest | CreateTextThreadWithoutMessageRequest


class ChannelsChannelIdWebhooksGetResponse(
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


class ChannelsChannelIdWebhooksPostRequest(BaseModel):
    name: Annotated[str, Field(max_length=80, min_length=1)]
    avatar: str | None = None


class ChannelsChannelIdMessagesMessageIdPatchRequest(MessageEditRequestPartial):
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


class ChannelsChannelIdMessagesPostRequest(MessageCreateRequest):
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
