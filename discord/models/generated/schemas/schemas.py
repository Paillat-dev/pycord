from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, RootModel

from ...flags import UserFlags


class AccessToken(RootModel[str]):
    root: Annotated[str, Field(max_length=152133)]


class AccountResponse(BaseModel):
    id: str
    name: str | None = None


class ActionRowComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    components: Annotated[
        list[
            ButtonComponentForMessageRequest
            | ChannelSelectComponentForMessageRequest
            | MentionableSelectComponentForMessageRequest
            | RoleSelectComponentForMessageRequest
            | StringSelectComponentForMessageRequest
            | UserSelectComponentForMessageRequest
        ],
        Field(max_length=5, min_length=1),
    ]


class ActionRowComponentForModalRequest(BaseModel):
    type: MessageComponentTypes
    components: Annotated[
        list[TextInputComponentForModalRequest], Field(max_length=5, min_length=1)
    ]


class ActionRowComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    components: (
        list[
            ButtonComponentResponse
            | ChannelSelectComponentResponse
            | MentionableSelectComponentResponse
            | RoleSelectComponentResponse
            | StringSelectComponentResponse
            | TextInputComponentResponse
            | UserSelectComponentResponse
        ]
        | None
    ) = None


class ActivitiesAttachmentResponse(BaseModel):
    attachment: AttachmentResponse


class AfkTimeouts(RootModel[int]):
    root: int


class AllowListItem(RootModel[str]):
    root: Annotated[str, Field(max_length=60, min_length=1)]


class AllowedMentionTypes(RootModel[str]):
    root: str


class ApplicationCommandAttachmentOption(BaseModel):
    type: ApplicationCommandOptionType
    name: Annotated[str, Field(max_length=32, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str, Field(max_length=100, min_length=1)]
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None


class ApplicationCommandAttachmentOptionResponse(BaseModel):
    type: ApplicationCommandOptionType
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    description: str
    description_localized: str | None = None
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None


class ApplicationCommandAutocompleteCallbackRequest(BaseModel):
    type: InteractionCallbackTypes
    data: (
        InteractionApplicationCommandAutocompleteCallbackIntegerData
        | InteractionApplicationCommandAutocompleteCallbackNumberData
        | InteractionApplicationCommandAutocompleteCallbackStringData
    )


class ApplicationCommandBooleanOption(BaseModel):
    type: ApplicationCommandOptionType
    name: Annotated[str, Field(max_length=32, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str, Field(max_length=100, min_length=1)]
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None


class ApplicationCommandBooleanOptionResponse(BaseModel):
    type: ApplicationCommandOptionType
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    description: str
    description_localized: str | None = None
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None


class ApplicationCommandChannelOption(BaseModel):
    type: ApplicationCommandOptionType
    name: Annotated[str, Field(max_length=32, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str, Field(max_length=100, min_length=1)]
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None
    channel_types: list[ChannelTypes] | None = None


class ApplicationCommandChannelOptionResponse(BaseModel):
    type: ApplicationCommandOptionType
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    description: str
    description_localized: str | None = None
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None
    channel_types: list[ChannelTypes] | None = None


class ApplicationCommandCreateRequest(BaseModel):
    name: Annotated[str, Field(max_length=32, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str | None, Field(max_length=100)] = None
    description_localizations: dict[str, Any] | None = None
    options: Annotated[
        list[
            ApplicationCommandAttachmentOption
            | ApplicationCommandBooleanOption
            | ApplicationCommandChannelOption
            | ApplicationCommandIntegerOption
            | ApplicationCommandMentionableOption
            | ApplicationCommandNumberOption
            | ApplicationCommandRoleOption
            | ApplicationCommandStringOption
            | ApplicationCommandSubcommandGroupOption
            | ApplicationCommandSubcommandOption
            | ApplicationCommandUserOption
        ]
        | None,
        Field(max_length=25),
    ] = None
    default_member_permissions: Annotated[
        int | None, Field(ge=0, le=2251799813685247)
    ] = None
    dm_permission: bool | None = None
    contexts: Annotated[list[InteractionContextType] | None, Field(min_length=1)] = None
    integration_types: Annotated[
        list[ApplicationIntegrationType] | None, Field(min_length=1)
    ] = None
    handler: ApplicationCommandHandler | None = None
    type: ApplicationCommandType | None = None


class ApplicationCommandHandler(RootModel[int]):
    root: int


class ApplicationCommandIntegerOption(BaseModel):
    type: ApplicationCommandOptionType
    name: Annotated[str, Field(max_length=32, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str, Field(max_length=100, min_length=1)]
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None
    autocomplete: bool | None = None
    choices: Annotated[
        list[ApplicationCommandOptionIntegerChoice] | None, Field(max_length=25)
    ] = None
    min_value: Int53Type | None = None
    max_value: Int53Type | None = None


class ApplicationCommandIntegerOptionResponse(BaseModel):
    type: ApplicationCommandOptionType
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    description: str
    description_localized: str | None = None
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None
    autocomplete: bool | None = None
    choices: list[ApplicationCommandOptionIntegerChoiceResponse] | None = None
    min_value: Int53Type | None = None
    max_value: Int53Type | None = None


class ApplicationCommandInteractionMetadataResponse(BaseModel):
    id: SnowflakeType
    type: InteractionTypes
    user: UserResponse | None = None
    authorizing_integration_owners: dict[str, SnowflakeType]
    original_response_message_id: SnowflakeType | None = None
    target_user: UserResponse | None = None
    target_message_id: SnowflakeType | None = None


class ApplicationCommandMentionableOption(BaseModel):
    type: ApplicationCommandOptionType
    name: Annotated[str, Field(max_length=32, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str, Field(max_length=100, min_length=1)]
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None


class ApplicationCommandMentionableOptionResponse(BaseModel):
    type: ApplicationCommandOptionType
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    description: str
    description_localized: str | None = None
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None


class ApplicationCommandNumberOption(BaseModel):
    type: ApplicationCommandOptionType
    name: Annotated[str, Field(max_length=32, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str, Field(max_length=100, min_length=1)]
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None
    autocomplete: bool | None = None
    choices: Annotated[
        list[ApplicationCommandOptionNumberChoice] | None, Field(max_length=25)
    ] = None
    min_value: float | None = None
    max_value: float | None = None


class ApplicationCommandNumberOptionResponse(BaseModel):
    type: ApplicationCommandOptionType
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    description: str
    description_localized: str | None = None
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None
    autocomplete: bool | None = None
    choices: list[ApplicationCommandOptionNumberChoiceResponse] | None = None
    min_value: float | None = None
    max_value: float | None = None


class ApplicationCommandOptionIntegerChoice(BaseModel):
    name: Annotated[str, Field(max_length=100, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    value: Int53Type


class ApplicationCommandOptionIntegerChoiceResponse(BaseModel):
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    value: Int53Type


class ApplicationCommandOptionNumberChoice(BaseModel):
    name: Annotated[str, Field(max_length=100, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    value: float


class ApplicationCommandOptionNumberChoiceResponse(BaseModel):
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    value: float


class ApplicationCommandOptionStringChoice(BaseModel):
    name: Annotated[str, Field(max_length=100, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    value: Annotated[str, Field(max_length=6000)]


class ApplicationCommandOptionStringChoiceResponse(BaseModel):
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    value: str


class ApplicationCommandOptionType(RootModel[int]):
    root: int


class ApplicationCommandPatchRequestPartial(BaseModel):
    name: Annotated[str | None, Field(max_length=32, min_length=1)] = None
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str | None, Field(max_length=100)] = None
    description_localizations: dict[str, Any] | None = None
    options: Annotated[
        list[
            ApplicationCommandAttachmentOption
            | ApplicationCommandBooleanOption
            | ApplicationCommandChannelOption
            | ApplicationCommandIntegerOption
            | ApplicationCommandMentionableOption
            | ApplicationCommandNumberOption
            | ApplicationCommandRoleOption
            | ApplicationCommandStringOption
            | ApplicationCommandSubcommandGroupOption
            | ApplicationCommandSubcommandOption
            | ApplicationCommandUserOption
        ]
        | None,
        Field(max_length=25),
    ] = None
    default_member_permissions: Annotated[
        int | None, Field(ge=0, le=2251799813685247)
    ] = None
    dm_permission: bool | None = None
    contexts: Annotated[list[InteractionContextType] | None, Field(min_length=1)] = None
    integration_types: Annotated[
        list[ApplicationIntegrationType] | None, Field(min_length=1)
    ] = None
    handler: ApplicationCommandHandler | None = None


class ApplicationCommandPermission(BaseModel):
    id: SnowflakeType
    type: ApplicationCommandPermissionType
    permission: bool


class ApplicationCommandPermissionType(RootModel[int]):
    root: int


class ApplicationCommandResponse(BaseModel):
    id: SnowflakeType
    application_id: SnowflakeType
    version: SnowflakeType
    default_member_permissions: str | None = None
    type: ApplicationCommandType
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    description: str
    description_localized: str | None = None
    description_localizations: dict[str, Any] | None = None
    guild_id: SnowflakeType | None = None
    dm_permission: bool | None = None
    contexts: list[InteractionContextType] | None = None
    integration_types: list[ApplicationIntegrationType] | None = None
    options: (
        list[
            ApplicationCommandAttachmentOptionResponse
            | ApplicationCommandBooleanOptionResponse
            | ApplicationCommandChannelOptionResponse
            | ApplicationCommandIntegerOptionResponse
            | ApplicationCommandMentionableOptionResponse
            | ApplicationCommandNumberOptionResponse
            | ApplicationCommandRoleOptionResponse
            | ApplicationCommandStringOptionResponse
            | ApplicationCommandSubcommandGroupOptionResponse
            | ApplicationCommandSubcommandOptionResponse
            | ApplicationCommandUserOptionResponse
        ]
        | None
    ) = None
    nsfw: bool | None = None


class ApplicationCommandRoleOption(BaseModel):
    type: ApplicationCommandOptionType
    name: Annotated[str, Field(max_length=32, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str, Field(max_length=100, min_length=1)]
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None


class ApplicationCommandRoleOptionResponse(BaseModel):
    type: ApplicationCommandOptionType
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    description: str
    description_localized: str | None = None
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None


class ApplicationCommandStringOption(BaseModel):
    type: ApplicationCommandOptionType
    name: Annotated[str, Field(max_length=32, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str, Field(max_length=100, min_length=1)]
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None
    autocomplete: bool | None = None
    min_length: Annotated[int | None, Field(ge=0, le=6000)] = None
    max_length: Annotated[int | None, Field(ge=1, le=6000)] = None
    choices: Annotated[
        list[ApplicationCommandOptionStringChoice] | None, Field(max_length=25)
    ] = None


class ApplicationCommandStringOptionResponse(BaseModel):
    type: ApplicationCommandOptionType
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    description: str
    description_localized: str | None = None
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None
    autocomplete: bool | None = None
    choices: list[ApplicationCommandOptionStringChoiceResponse] | None = None
    min_length: int | None = None
    max_length: int | None = None


class ApplicationCommandSubcommandGroupOption(BaseModel):
    type: ApplicationCommandOptionType
    name: Annotated[str, Field(max_length=32, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str, Field(max_length=100, min_length=1)]
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None
    options: Annotated[
        list[ApplicationCommandSubcommandOption] | None, Field(max_length=25)
    ] = None


class ApplicationCommandSubcommandGroupOptionResponse(BaseModel):
    type: ApplicationCommandOptionType
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    description: str
    description_localized: str | None = None
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None
    options: list[ApplicationCommandSubcommandOptionResponse] | None = None


class ApplicationCommandSubcommandOption(BaseModel):
    type: ApplicationCommandOptionType
    name: Annotated[str, Field(max_length=32, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str, Field(max_length=100, min_length=1)]
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None
    options: Annotated[
        list[
            ApplicationCommandAttachmentOption
            | ApplicationCommandBooleanOption
            | ApplicationCommandChannelOption
            | ApplicationCommandIntegerOption
            | ApplicationCommandMentionableOption
            | ApplicationCommandNumberOption
            | ApplicationCommandRoleOption
            | ApplicationCommandStringOption
            | ApplicationCommandUserOption
        ]
        | None,
        Field(max_length=25),
    ] = None


class ApplicationCommandSubcommandOptionResponse(BaseModel):
    type: ApplicationCommandOptionType
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    description: str
    description_localized: str | None = None
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None
    options: (
        list[
            ApplicationCommandAttachmentOptionResponse
            | ApplicationCommandBooleanOptionResponse
            | ApplicationCommandChannelOptionResponse
            | ApplicationCommandIntegerOptionResponse
            | ApplicationCommandMentionableOptionResponse
            | ApplicationCommandNumberOptionResponse
            | ApplicationCommandRoleOptionResponse
            | ApplicationCommandStringOptionResponse
            | ApplicationCommandUserOptionResponse
        ]
        | None
    ) = None


class ApplicationCommandType(RootModel[int]):
    root: int


class ApplicationCommandUpdateRequest(BaseModel):
    name: Annotated[str, Field(max_length=32, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str | None, Field(max_length=100)] = None
    description_localizations: dict[str, Any] | None = None
    options: Annotated[
        list[
            ApplicationCommandAttachmentOption
            | ApplicationCommandBooleanOption
            | ApplicationCommandChannelOption
            | ApplicationCommandIntegerOption
            | ApplicationCommandMentionableOption
            | ApplicationCommandNumberOption
            | ApplicationCommandRoleOption
            | ApplicationCommandStringOption
            | ApplicationCommandSubcommandGroupOption
            | ApplicationCommandSubcommandOption
            | ApplicationCommandUserOption
        ]
        | None,
        Field(max_length=25),
    ] = None
    default_member_permissions: Annotated[
        int | None, Field(ge=0, le=2251799813685247)
    ] = None
    dm_permission: bool | None = None
    contexts: Annotated[list[InteractionContextType] | None, Field(min_length=1)] = None
    integration_types: Annotated[
        list[ApplicationIntegrationType] | None, Field(min_length=1)
    ] = None
    handler: ApplicationCommandHandler | None = None
    type: ApplicationCommandType | None = None
    id: SnowflakeType | None = None


class ApplicationCommandUserOption(BaseModel):
    type: ApplicationCommandOptionType
    name: Annotated[str, Field(max_length=32, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str, Field(max_length=100, min_length=1)]
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None


class ApplicationCommandUserOptionResponse(BaseModel):
    type: ApplicationCommandOptionType
    name: str
    name_localized: str | None = None
    name_localizations: dict[str, Any] | None = None
    description: str
    description_localized: str | None = None
    description_localizations: dict[str, Any] | None = None
    required: bool | None = None


class ApplicationExplicitContentFilterTypes(RootModel[int]):
    root: int


class ApplicationFormPartial(BaseModel):
    description: Description | None = None
    icon: str | None = None
    cover_image: str | None = None
    team_id: SnowflakeType | None = None
    flags: int | None = None
    interactions_endpoint_url: AnyUrl | None = None
    explicit_content_filter: ApplicationExplicitContentFilterTypes | None = None
    max_participants: Annotated[int | None, Field(ge=-1)] = None
    type: ApplicationTypes | None = None
    tags: Annotated[list[Tag] | None, Field(max_length=5)] = None
    custom_install_url: AnyUrl | None = None
    install_params: ApplicationOAuth2InstallParams | None = None
    role_connections_verification_url: AnyUrl | None = None
    integration_types_config: dict[str, Any] | None = None


class ApplicationIdentityProviderAuthType(RootModel[str]):
    root: str


class ApplicationIncomingWebhookResponse(BaseModel):
    application_id: SnowflakeType | None = None
    avatar: str | None = None
    channel_id: SnowflakeType | None = None
    guild_id: SnowflakeType | None = None
    id: SnowflakeType
    name: str
    type: WebhookTypes
    user: UserResponse | None = None


class ApplicationIntegrationType(RootModel[int]):
    root: int


class ApplicationIntegrationTypeConfiguration(BaseModel):
    oauth2_install_params: ApplicationOAuth2InstallParams | None = None


class ApplicationIntegrationTypeConfigurationResponse(BaseModel):
    oauth2_install_params: ApplicationOAuth2InstallParamsResponse | None = None


class ApplicationOAuth2InstallParams(BaseModel):
    scopes: Annotated[list[OAuth2Scopes] | None, Field(min_length=1)] = None
    permissions: Annotated[int | None, Field(ge=0, le=2251799813685247)] = None


class ApplicationOAuth2InstallParamsResponse(BaseModel):
    scopes: list[OAuth2Scopes]
    permissions: str


class ApplicationResponse(BaseModel):
    id: SnowflakeType
    name: str
    icon: str | None = None
    description: str
    type: ApplicationTypes | None = None
    cover_image: str | None = None
    primary_sku_id: SnowflakeType | None = None
    bot: UserResponse | None = None
    slug: str | None = None
    guild_id: SnowflakeType | None = None
    rpc_origins: list[str | None] | None = None
    bot_public: bool | None = None
    bot_require_code_grant: bool | None = None
    terms_of_service_url: AnyUrl | None = None
    privacy_policy_url: AnyUrl | None = None
    custom_install_url: AnyUrl | None = None
    install_params: ApplicationOAuth2InstallParamsResponse | None = None
    integration_types_config: dict[str, Any] | None = None
    verify_key: str
    flags: int
    max_participants: int | None = None
    tags: list[str] | None = None


class ApplicationRoleConnectionsMetadataItemRequest(BaseModel):
    type: MetadataItemTypes
    key: Annotated[str, Field(max_length=50, min_length=1)]
    name: Annotated[str, Field(max_length=100, min_length=1)]
    name_localizations: dict[str, Any] | None = None
    description: Annotated[str, Field(max_length=200, min_length=1)]
    description_localizations: dict[str, Any] | None = None


class ApplicationRoleConnectionsMetadataItemResponse(BaseModel):
    type: MetadataItemTypes
    key: str
    name: str
    name_localizations: dict[str, Any] | None = None
    description: str
    description_localizations: dict[str, Any] | None = None


class ApplicationTypes(RootModel[int]):
    root: int


class ApplicationUserRoleConnectionResponse(BaseModel):
    platform_name: str | None = None
    platform_username: str | None = None
    metadata: dict[str, Any] | None = None


class AttachmentResponse(BaseModel):
    id: SnowflakeType
    filename: str
    size: int
    url: AnyUrl
    proxy_url: AnyUrl
    width: int | None = None
    height: int | None = None
    duration_secs: float | None = None
    waveform: str | None = None
    description: str | None = None
    content_type: str | None = None
    ephemeral: bool | None = None
    title: str | None = None
    application: ApplicationResponse | None = None
    clip_created_at: datetime | None = None
    clip_participants: list[UserResponse] | None = None


class AuditLogActionTypes(RootModel[int]):
    root: int


class AuditLogEntryResponse(BaseModel):
    id: SnowflakeType
    action_type: AuditLogActionTypes
    user_id: SnowflakeType | None = None
    target_id: SnowflakeType | None = None
    changes: list[AuditLogObjectChangeResponse] | None = None
    options: dict[str, Any] | None = None
    reason: str | None = None


class AuditLogObjectChangeResponse(BaseModel):
    key: str | None = None
    new_value: Any | None = None
    old_value: Any | None = None


class AutomodActionType(RootModel[int]):
    root: int


class AutomodEventType(RootModel[int]):
    root: int


class AutomodKeywordPresetType(RootModel[int]):
    root: int


class AutomodTriggerType(RootModel[int]):
    root: int


class AvailableLocalesEnum(RootModel[str]):
    root: str


class BaseCreateMessageCreateRequest(BaseModel):
    content: Annotated[str | None, Field(max_length=4000)] = None
    embeds: Annotated[list[RichEmbed] | None, Field(max_length=10)] = None
    allowed_mentions: MessageAllowedMentionsRequest | None = None
    sticker_ids: Annotated[list[SnowflakeType] | None, Field(max_length=3)] = None
    components: Annotated[
        list[
            ActionRowComponentForMessageRequest
            | ContainerComponentForMessageRequest
            | FileComponentForMessageRequest
            | MediaGalleryComponentForMessageRequest
            | SectionComponentForMessageRequest
            | SeparatorComponentForMessageRequest
            | TextDisplayComponentForMessageRequest
        ]
        | None,
        Field(max_length=40),
    ] = None
    flags: int | None = None
    attachments: Annotated[
        list[MessageAttachmentRequest] | None, Field(max_length=10)
    ] = None
    poll: PollCreateRequest | None = None
    confetti_potion: ConfettiPotionCreateRequest | None = None


class BasicApplicationResponse(BaseModel):
    id: SnowflakeType
    name: str
    icon: str | None = None
    description: str
    type: ApplicationTypes | None = None
    cover_image: str | None = None
    primary_sku_id: SnowflakeType | None = None
    bot: UserResponse | None = None


class BasicMessageResponse(BaseModel):
    type: MessageType
    content: str
    mentions: list[UserResponse]
    mention_roles: list[SnowflakeType]
    attachments: list[MessageAttachmentResponse]
    embeds: list[MessageEmbedResponse]
    timestamp: datetime
    edited_timestamp: datetime | None = None
    flags: int
    components: list[
        ActionRowComponentResponse
        | ContainerComponentResponse
        | FileComponentResponse
        | MediaGalleryComponentResponse
        | SectionComponentResponse
        | SeparatorComponentResponse
        | TextDisplayComponentResponse
    ]
    resolved: ResolvedObjectsResponse | None = None
    stickers: list[GuildStickerResponse | StandardStickerResponse] | None = None
    sticker_items: list[MessageStickerItemResponse] | None = None
    id: SnowflakeType
    channel_id: SnowflakeType
    author: UserResponse
    pinned: bool
    mention_everyone: bool
    tts: bool
    call: MessageCallResponse | None = None
    activity: MessageActivityResponse | None = None
    application: BasicApplicationResponse | None = None
    application_id: SnowflakeType | None = None
    interaction: MessageInteractionResponse | None = None
    nonce: Nonce | Nonce1 | None = None
    webhook_id: SnowflakeType | None = None
    message_reference: MessageReferenceResponse | None = None
    thread: ThreadResponse | None = None
    mention_channels: list[MessageMentionChannelResponse | None] | None = None
    role_subscription_data: MessageRoleSubscriptionDataResponse | None = None
    purchase_notification: PurchaseNotificationResponse | None = None
    position: int | None = None
    poll: PollResponse | None = None
    interaction_metadata: (
        ApplicationCommandInteractionMetadataResponse
        | MessageComponentInteractionMetadataResponse
        | ModalSubmitInteractionMetadataResponse
        | None
    ) = None
    message_snapshots: list[MessageSnapshotResponse] | None = None


class BlockMessageAction(BaseModel):
    type: AutomodActionType
    metadata: BlockMessageActionMetadata | None = None


class BlockMessageActionMetadata(BaseModel):
    custom_message: Annotated[str | None, Field(max_length=150)] = None


class BlockMessageActionMetadataResponse(BaseModel):
    custom_message: str | None = None


class BlockMessageActionResponse(BaseModel):
    type: AutomodActionType
    metadata: BlockMessageActionMetadataResponse


class BotAccountPatchRequest(BaseModel):
    username: Annotated[str, Field(max_length=32, min_length=2)]
    avatar: str | None = None
    banner: str | None = None


class BulkBanUsersResponse(BaseModel):
    banned_users: list[SnowflakeType]
    failed_users: list[SnowflakeType]


class ButtonComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    custom_id: Annotated[str | None, Field(max_length=100)] = None
    style: ButtonStyleTypes
    label: Annotated[str | None, Field(max_length=80)] = None
    disabled: bool | None = None
    url: AnyUrl | None = None
    sku_id: SnowflakeType | None = None
    emoji: ComponentEmojiForMessageRequest | None = None


class ButtonComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    custom_id: str | None = None
    style: ButtonStyleTypes
    label: str | None = None
    disabled: bool | None = None
    emoji: ComponentEmojiResponse | None = None
    url: AnyUrl | None = None
    sku_id: SnowflakeType | None = None


class ButtonStyleTypes(RootModel[int]):
    root: int


class ChannelFollowerResponse(BaseModel):
    channel_id: SnowflakeType
    webhook_id: SnowflakeType


class ChannelFollowerWebhookResponse(BaseModel):
    application_id: SnowflakeType | None = None
    avatar: str | None = None
    channel_id: SnowflakeType | None = None
    guild_id: SnowflakeType | None = None
    id: SnowflakeType
    name: str
    type: WebhookTypes
    user: UserResponse | None = None
    source_guild: WebhookSourceGuildResponse | None = None
    source_channel: WebhookSourceChannelResponse | None = None


class ChannelPermissionOverwriteRequest(BaseModel):
    id: SnowflakeType
    type: ChannelPermissionOverwrites | None = None
    allow: int | None = None
    deny: int | None = None


class ChannelPermissionOverwriteResponse(BaseModel):
    id: SnowflakeType
    type: ChannelPermissionOverwrites
    allow: str
    deny: str


class ChannelPermissionOverwrites(RootModel[int]):
    root: int


class ChannelSelectComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    custom_id: Annotated[str, Field(max_length=100)]
    placeholder: Annotated[str | None, Field(max_length=150)] = None
    min_values: Annotated[int | None, Field(ge=0, le=25)] = None
    max_values: Annotated[int | None, Field(ge=1, le=25)] = None
    disabled: bool | None = None
    default_values: Annotated[
        list[ChannelSelectDefaultValue] | None, Field(max_length=25)
    ] = None
    channel_types: list[ChannelTypes] | None = None


class ChannelSelectComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    custom_id: str
    placeholder: str | None = None
    min_values: int | None = None
    max_values: int | None = None
    disabled: bool | None = None
    channel_types: list[ChannelTypes] | None = None
    default_values: list[ChannelSelectDefaultValueResponse] | None = None


class ChannelSelectDefaultValue(BaseModel):
    type: SnowflakeSelectDefaultValueTypes
    id: SnowflakeType


class ChannelSelectDefaultValueResponse(BaseModel):
    type: SnowflakeSelectDefaultValueTypes
    id: SnowflakeType


class ChannelTypes(RootModel[int]):
    root: int


class CommandPermissionResponse(BaseModel):
    id: SnowflakeType
    type: ApplicationCommandPermissionType
    permission: bool


class CommandPermissionsResponse(BaseModel):
    id: SnowflakeType
    application_id: SnowflakeType
    guild_id: SnowflakeType
    permissions: list[CommandPermissionResponse]


class ComponentEmojiForMessageRequest(BaseModel):
    id: SnowflakeType | None = None
    name: Annotated[str, Field(max_length=32)]


class ComponentEmojiResponse(BaseModel):
    id: SnowflakeType | None = None
    name: str
    animated: bool | None = None


class ConfettiPotionCreateRequest(BaseModel):
    pass


class ConnectedAccountGuildResponse(BaseModel):
    id: SnowflakeType
    name: str
    icon: str | None = None


class ConnectedAccountIntegrationResponse(BaseModel):
    id: str
    type: IntegrationTypes
    account: AccountResponse
    guild: ConnectedAccountGuildResponse


class ConnectedAccountProviders(RootModel[str]):
    root: str


class ConnectedAccountResponse(BaseModel):
    id: str
    name: str | None = None
    type: ConnectedAccountProviders
    friend_sync: bool
    integrations: list[ConnectedAccountIntegrationResponse] | None = None
    show_activity: bool
    two_way_link: bool
    verified: bool
    visibility: ConnectedAccountVisibility
    revoked: bool | None = None


class ConnectedAccountVisibility(RootModel[int]):
    root: int


class ContainerComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    accent_color: Annotated[int | None, Field(ge=0, le=16777215)] = None
    components: Annotated[
        list[
            ActionRowComponentForMessageRequest
            | FileComponentForMessageRequest
            | MediaGalleryComponentForMessageRequest
            | SectionComponentForMessageRequest
            | SeparatorComponentForMessageRequest
            | TextDisplayComponentForMessageRequest
        ],
        Field(max_length=40, min_length=1),
    ]
    spoiler: bool | None = None


class ContainerComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    accent_color: int | None = None
    components: list[
        ActionRowComponentResponse
        | FileComponentResponse
        | MediaGalleryComponentResponse
        | SectionComponentResponse
        | SeparatorComponentResponse
        | TextDisplayComponentResponse
    ]
    spoiler: bool


class CreateEntitlementRequestData(BaseModel):
    sku_id: SnowflakeType
    owner_id: SnowflakeType
    owner_type: EntitlementOwnerTypes


class CreateForumThreadRequest(BaseModel):
    name: Annotated[str, Field(max_length=100, min_length=1)]
    auto_archive_duration: ThreadAutoArchiveDuration | None = None
    rate_limit_per_user: Annotated[int | None, Field(ge=0, le=21600)] = None
    applied_tags: Annotated[list[SnowflakeType] | None, Field(max_length=5)] = None
    message: BaseCreateMessageCreateRequest


class CreateGroupDMInviteRequest(BaseModel):
    max_age: Annotated[int | None, Field(ge=1, le=604800)] = None


class CreateGuildChannelRequest(BaseModel):
    type: ChannelTypes | None = None
    name: Annotated[str, Field(max_length=100, min_length=1)]
    position: Annotated[int | None, Field(ge=0)] = None
    topic: Annotated[str | None, Field(max_length=4096, min_length=0)] = None
    bitrate: Annotated[int | None, Field(ge=8000)] = None
    user_limit: Annotated[int | None, Field(ge=0)] = None
    nsfw: bool | None = None
    rate_limit_per_user: Annotated[int | None, Field(ge=0, le=21600)] = None
    parent_id: SnowflakeType | None = None
    permission_overwrites: Annotated[
        list[ChannelPermissionOverwriteRequest] | None, Field(max_length=100)
    ] = None
    rtc_region: str | None = None
    video_quality_mode: VideoQualityModes | None = None
    default_auto_archive_duration: ThreadAutoArchiveDuration | None = None
    default_reaction_emoji: UpdateDefaultReactionEmojiRequest | None = None
    default_thread_rate_limit_per_user: Annotated[int | None, Field(ge=0, le=21600)] = (
        None
    )
    default_sort_order: ThreadSortOrder | None = None
    default_forum_layout: ForumLayout | None = None
    default_tag_setting: ThreadSearchTagSetting | None = None
    available_tags: Annotated[
        list[CreateOrUpdateThreadTagRequest | None] | None, Field(max_length=20)
    ] = None


class CreateGuildInviteRequest(BaseModel):
    max_age: Annotated[int | None, Field(ge=0, le=604800)] = None
    temporary: bool | None = None
    max_uses: Annotated[int | None, Field(ge=0, le=100)] = None
    unique: bool | None = None
    target_user_id: SnowflakeType | None = None
    target_application_id: SnowflakeType | None = None
    target_type: InviteTargetTypes | None = None


class CreateGuildRequestChannelItem(BaseModel):
    type: ChannelTypes | None = None
    name: Annotated[str, Field(max_length=100, min_length=1)]
    position: Annotated[int | None, Field(ge=0)] = None
    topic: Annotated[str | None, Field(max_length=4096, min_length=0)] = None
    bitrate: Annotated[int | None, Field(ge=8000)] = None
    user_limit: Annotated[int | None, Field(ge=0)] = None
    nsfw: bool | None = None
    rate_limit_per_user: Annotated[int | None, Field(ge=0, le=21600)] = None
    parent_id: SnowflakeType | None = None
    permission_overwrites: Annotated[
        list[ChannelPermissionOverwriteRequest] | None, Field(max_length=100)
    ] = None
    rtc_region: str | None = None
    video_quality_mode: VideoQualityModes | None = None
    default_auto_archive_duration: ThreadAutoArchiveDuration | None = None
    default_reaction_emoji: UpdateDefaultReactionEmojiRequest | None = None
    default_thread_rate_limit_per_user: Annotated[int | None, Field(ge=0, le=21600)] = (
        None
    )
    default_sort_order: ThreadSortOrder | None = None
    default_forum_layout: ForumLayout | None = None
    default_tag_setting: ThreadSearchTagSetting | None = None
    id: SnowflakeType | None = None
    available_tags: Annotated[
        list[CreateOrUpdateThreadTagRequest] | None, Field(max_length=20)
    ] = None


class CreateGuildRequestRoleItem(BaseModel):
    id: int
    name: Annotated[str | None, Field(max_length=100)] = None
    permissions: int | None = None
    color: Annotated[int | None, Field(ge=0, le=16777215)] = None
    hoist: bool | None = None
    mentionable: bool | None = None
    unicode_emoji: Annotated[str | None, Field(max_length=100)] = None


class CreateMessageInteractionCallbackRequest(BaseModel):
    type: InteractionCallbackTypes
    data: IncomingWebhookInteractionRequest | None = None


class CreateMessageInteractionCallbackResponse(BaseModel):
    type: InteractionCallbackTypes
    message: MessageResponse


class CreateOrUpdateThreadTagRequest(BaseModel):
    name: Annotated[str, Field(max_length=20, min_length=0)]
    emoji_id: SnowflakeType | None = None
    emoji_name: Annotated[str | None, Field(max_length=100)] = None
    moderated: bool | None = None


class CreatePrivateChannelRequest(BaseModel):
    recipient_id: SnowflakeType | None = None
    access_tokens: Annotated[list[AccessToken] | None, Field(max_length=1521)] = None
    nicks: dict[str, Any] | None = None


class CreateTextThreadWithMessageRequest(BaseModel):
    name: Annotated[str, Field(max_length=100, min_length=1)]
    auto_archive_duration: ThreadAutoArchiveDuration | None = None
    rate_limit_per_user: Annotated[int | None, Field(ge=0, le=21600)] = None


class CreateTextThreadWithoutMessageRequest(BaseModel):
    name: Annotated[str, Field(max_length=100, min_length=1)]
    auto_archive_duration: ThreadAutoArchiveDuration | None = None
    rate_limit_per_user: Annotated[int | None, Field(ge=0, le=21600)] = None
    type: ChannelTypes | None = None
    invitable: bool | None = None


class CreatedThreadResponse(BaseModel):
    id: SnowflakeType
    type: ChannelTypes
    last_message_id: SnowflakeType | None = None
    flags: int
    last_pin_timestamp: datetime | None = None
    guild_id: SnowflakeType
    name: str
    parent_id: SnowflakeType | None = None
    rate_limit_per_user: int | None = None
    bitrate: int | None = None
    user_limit: int | None = None
    rtc_region: str | None = None
    video_quality_mode: VideoQualityModes | None = None
    permissions: str | None = None
    owner_id: SnowflakeType
    thread_metadata: ThreadMetadataResponse | None = None
    message_count: int
    member_count: int
    total_message_sent: int
    applied_tags: list[SnowflakeType] | None = None
    member: ThreadMemberResponse | None = None


class DefaultKeywordListTriggerMetadata(BaseModel):
    allow_list: Annotated[list[AllowListItem] | None, Field(max_length=1000)] = None
    presets: list[AutomodKeywordPresetType] | None = None


class DefaultKeywordListTriggerMetadataResponse(BaseModel):
    allow_list: list[str]
    presets: list[AutomodKeywordPresetType]


class DefaultKeywordListUpsertRequest(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    event_type: AutomodEventType
    actions: Annotated[
        list[
            BlockMessageAction
            | FlagToChannelAction
            | QuarantineUserAction
            | UserCommunicationDisabledAction
        ]
        | None,
        Field(max_length=5, min_length=1),
    ] = None
    enabled: bool | None = None
    exempt_roles: Annotated[list[SnowflakeType] | None, Field(max_length=20)] = None
    exempt_channels: Annotated[list[SnowflakeType] | None, Field(max_length=50)] = None
    trigger_type: AutomodTriggerType
    trigger_metadata: DefaultKeywordListTriggerMetadata


class DefaultKeywordListUpsertRequestPartial(BaseModel):
    name: Annotated[str | None, Field(max_length=100)] = None
    event_type: AutomodEventType | None = None
    actions: Annotated[
        list[
            BlockMessageAction
            | FlagToChannelAction
            | QuarantineUserAction
            | UserCommunicationDisabledAction
        ]
        | None,
        Field(max_length=5, min_length=1),
    ] = None
    enabled: bool | None = None
    exempt_roles: Annotated[list[SnowflakeType] | None, Field(max_length=20)] = None
    exempt_channels: Annotated[list[SnowflakeType] | None, Field(max_length=50)] = None
    trigger_type: AutomodTriggerType | None = None
    trigger_metadata: DefaultKeywordListTriggerMetadata | None = None


class DefaultKeywordRuleResponse(BaseModel):
    id: SnowflakeType
    guild_id: SnowflakeType
    creator_id: SnowflakeType
    name: str
    event_type: AutomodEventType
    actions: list[
        BlockMessageActionResponse
        | FlagToChannelActionResponse
        | QuarantineUserActionResponse
        | UserCommunicationDisabledActionResponse
    ]
    trigger_type: AutomodTriggerType
    enabled: bool | None = None
    exempt_roles: list[SnowflakeType] | None = None
    exempt_channels: list[SnowflakeType] | None = None
    trigger_metadata: DefaultKeywordListTriggerMetadataResponse


class DefaultReactionEmojiResponse(BaseModel):
    emoji_id: SnowflakeType | None = None
    emoji_name: str | None = None


class Description(BaseModel):
    default: Annotated[str, Field(max_length=400)]
    localizations: dict[str, Any] | None = None


class DiscordIntegrationResponse(BaseModel):
    type: IntegrationTypes
    name: str | None = None
    account: AccountResponse | None = None
    enabled: bool | None = None
    id: SnowflakeType
    application: IntegrationApplicationResponse
    scopes: list[OAuth2Scopes]
    user: UserResponse | None = None


class EmbeddedActivityInstance(BaseModel):
    application_id: SnowflakeType
    instance_id: str
    launch_id: str
    location: GuildChannelLocation | PrivateChannelLocation | None = None
    users: list[SnowflakeType]


class EmbeddedActivityLocationKind(RootModel[str]):
    root: str


class EmojiResponse(BaseModel):
    id: SnowflakeType
    name: str
    user: UserResponse | None = None
    roles: list[SnowflakeType]
    require_colons: bool
    managed: bool
    animated: bool
    available: bool


class EntitlementOwnerTypes(RootModel[int]):
    root: int


class EntitlementResponse(BaseModel):
    id: SnowflakeType
    sku_id: SnowflakeType
    application_id: SnowflakeType
    user_id: SnowflakeType
    guild_id: SnowflakeType | None = None
    deleted: bool
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    type: EntitlementTypes
    fulfilled_at: datetime | None = None
    fulfillment_status: EntitlementTenantFulfillmentStatusResponse | None = None
    consumed: bool | None = None


class EntitlementTenantFulfillmentStatusResponse(RootModel[int]):
    root: int


class EntitlementTypes(RootModel[int]):
    root: int


class EntityMetadataExternal(BaseModel):
    location: Annotated[str, Field(max_length=100)]


class EntityMetadataExternalResponse(BaseModel):
    location: str


class EntityMetadataStageInstance(BaseModel):
    pass


class EntityMetadataStageInstanceResponse(BaseModel):
    pass


class EntityMetadataVoice(BaseModel):
    pass


class EntityMetadataVoiceResponse(BaseModel):
    pass


class Error(BaseModel):
    """A single error, either for an API response or a specific field."""

    code: int
    """\n    Discord internal error code. See error code reference\n"""
    message: str
    """\n    Human-readable error message\n"""


class ErrorDetails(RootModel["dict[str, ErrorDetails] | InnerErrors"]):
    root: dict[str, ErrorDetails] | InnerErrors


class ErrorResponse(Error):
    """Errors object returned by the Discord API"""

    errors: ErrorDetails | None = None


class ExternalConnectionIntegrationResponse(BaseModel):
    type: IntegrationTypes
    name: str | None = None
    account: AccountResponse | None = None
    enabled: bool | None = None
    id: str
    user: UserResponse
    revoked: bool | None = None
    expire_behavior: IntegrationExpireBehaviorTypes | None = None
    expire_grace_period: IntegrationExpireGracePeriodTypes | None = None
    subscriber_count: int | None = None
    synced_at: datetime | None = None
    role_id: SnowflakeType | None = None
    syncing: bool | None = None
    enable_emoticons: bool | None = None


class ExternalScheduledEventCreateRequest(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    description: Annotated[str | None, Field(max_length=1000)] = None
    image: str | None = None
    scheduled_start_time: datetime
    scheduled_end_time: datetime | None = None
    privacy_level: GuildScheduledEventPrivacyLevels
    entity_type: GuildScheduledEventEntityTypes
    channel_id: SnowflakeType | None = None
    entity_metadata: EntityMetadataExternal


class ExternalScheduledEventPatchRequestPartial(BaseModel):
    status: GuildScheduledEventStatuses | None = None
    name: Annotated[str | None, Field(max_length=100)] = None
    description: Annotated[str | None, Field(max_length=1000)] = None
    image: str | None = None
    scheduled_start_time: datetime | None = None
    scheduled_end_time: datetime | None = None
    entity_type: GuildScheduledEventEntityTypes | None = None
    privacy_level: GuildScheduledEventPrivacyLevels | None = None
    channel_id: SnowflakeType | None = None
    entity_metadata: EntityMetadataExternal | None = None


class ExternalScheduledEventResponse(BaseModel):
    id: SnowflakeType
    guild_id: SnowflakeType
    name: str
    description: str | None = None
    channel_id: SnowflakeType | None = None
    creator_id: SnowflakeType | None = None
    creator: UserResponse | None = None
    image: str | None = None
    scheduled_start_time: datetime
    scheduled_end_time: datetime | None = None
    status: GuildScheduledEventStatuses
    entity_type: GuildScheduledEventEntityTypes
    entity_id: SnowflakeType | None = None
    user_count: int | None = None
    privacy_level: GuildScheduledEventPrivacyLevels
    user_rsvp: ScheduledEventUserResponse | None = None
    entity_metadata: EntityMetadataExternalResponse


class Feature(RootModel[str | None]):
    root: Annotated[str | None, Field(max_length=152133)]


class FileComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    spoiler: bool | None = None
    file: UnfurledMediaRequestWithAttachmentReferenceRequired


class FileComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    file: UnfurledMediaResponse
    name: str | None = None
    size: int | None = None
    spoiler: bool


class FlagToChannelAction(BaseModel):
    type: AutomodActionType
    metadata: FlagToChannelActionMetadata


class FlagToChannelActionMetadata(BaseModel):
    channel_id: SnowflakeType


class FlagToChannelActionMetadataResponse(BaseModel):
    channel_id: SnowflakeType


class FlagToChannelActionResponse(BaseModel):
    type: AutomodActionType
    metadata: FlagToChannelActionMetadataResponse


class Flags(int, Enum):
    integer_1 = 1


class ForumLayout(RootModel[int]):
    root: int


class ForumTagResponse(BaseModel):
    id: SnowflakeType
    name: str
    moderated: bool
    emoji_id: SnowflakeType | None = None
    emoji_name: str | None = None


class FriendInviteResponse(BaseModel):
    type: InviteTypes | None = None
    code: str
    inviter: UserResponse | None = None
    max_age: int | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None
    friends_count: int | None = None
    channel: InviteChannelResponse | None = None
    is_contact: bool | None = None
    uses: int | None = None
    max_uses: int | None = None
    flags: int | None = None


class GatewayBotResponse(BaseModel):
    url: AnyUrl
    session_start_limit: GatewayBotSessionStartLimitResponse
    shards: int


class GatewayBotSessionStartLimitResponse(BaseModel):
    max_concurrency: int
    remaining: int
    reset_after: int
    total: int


class GatewayResponse(BaseModel):
    url: AnyUrl


class GithubAuthor(BaseModel):
    username: Annotated[str | None, Field(max_length=152133)] = None
    name: Annotated[str, Field(max_length=152133)]


class GithubCheckApp(BaseModel):
    name: Annotated[str, Field(max_length=152133)]


class GithubCheckPullRequest(BaseModel):
    number: int


class GithubCheckRun(BaseModel):
    conclusion: Annotated[str | None, Field(max_length=152133)] = None
    name: Annotated[str, Field(max_length=152133)]
    html_url: AnyUrl
    check_suite: GithubCheckSuite
    details_url: AnyUrl | None = None
    output: GithubCheckRunOutput | None = None
    pull_requests: Annotated[
        list[GithubCheckPullRequest] | None, Field(max_length=1521)
    ] = None


class GithubCheckRunOutput(BaseModel):
    title: Annotated[str | None, Field(max_length=152133)] = None
    summary: Annotated[str | None, Field(max_length=152133)] = None


class GithubCheckSuite(BaseModel):
    conclusion: Annotated[str | None, Field(max_length=152133)] = None
    head_branch: Annotated[str | None, Field(max_length=152133)] = None
    head_sha: Annotated[str, Field(max_length=152133)]
    pull_requests: Annotated[
        list[GithubCheckPullRequest] | None, Field(max_length=1521)
    ] = None
    app: GithubCheckApp


class GithubComment(BaseModel):
    id: int
    html_url: AnyUrl
    user: GithubUser
    commit_id: Annotated[str | None, Field(max_length=152133)] = None
    body: Annotated[str, Field(max_length=152133)]


class GithubCommit(BaseModel):
    id: Annotated[str, Field(max_length=152133)]
    url: AnyUrl
    message: Annotated[str, Field(max_length=152133)]
    author: GithubAuthor


class GithubDiscussion(BaseModel):
    title: Annotated[str, Field(max_length=152133)]
    number: int
    html_url: AnyUrl
    answer_html_url: AnyUrl | None = None
    body: Annotated[str | None, Field(max_length=152133)] = None
    user: GithubUser


class GithubIssue(BaseModel):
    id: int
    number: int
    html_url: AnyUrl
    user: GithubUser
    title: Annotated[str, Field(max_length=152133)]
    body: Annotated[str | None, Field(max_length=152133)] = None
    pull_request: Any | None = None


class GithubRelease(BaseModel):
    id: int
    tag_name: Annotated[str, Field(max_length=152133)]
    html_url: AnyUrl
    author: GithubUser


class GithubRepository(BaseModel):
    id: int
    html_url: AnyUrl
    name: Annotated[str, Field(max_length=152133)]
    full_name: Annotated[str, Field(max_length=152133)]


class GithubReview(BaseModel):
    user: GithubUser
    body: Annotated[str | None, Field(max_length=152133)] = None
    html_url: AnyUrl
    state: Annotated[str, Field(max_length=152133)]


class GithubUser(BaseModel):
    id: int
    login: Annotated[str, Field(max_length=152133)]
    html_url: AnyUrl
    avatar_url: AnyUrl


class GithubWebhook(BaseModel):
    action: Annotated[str | None, Field(max_length=152133)] = None
    ref: Annotated[str | None, Field(max_length=152133)] = None
    ref_type: Annotated[str | None, Field(max_length=152133)] = None
    comment: GithubComment | None = None
    issue: GithubIssue | None = None
    pull_request: GithubIssue | None = None
    repository: GithubRepository | None = None
    forkee: GithubRepository | None = None
    sender: GithubUser
    member: GithubUser | None = None
    release: GithubRelease | None = None
    head_commit: GithubCommit | None = None
    commits: Annotated[list[GithubCommit] | None, Field(max_length=1521)] = None
    forced: bool | None = None
    compare: AnyUrl | None = None
    review: GithubReview | None = None
    check_run: GithubCheckRun | None = None
    check_suite: GithubCheckSuite | None = None
    discussion: GithubDiscussion | None = None
    answer: GithubComment | None = None


class GroupDMInviteResponse(BaseModel):
    type: InviteTypes | None = None
    code: str
    inviter: UserResponse | None = None
    max_age: int | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None
    channel: InviteChannelResponse | None = None
    approximate_member_count: int | None = None


class GuildAuditLogResponse(BaseModel):
    audit_log_entries: list[AuditLogEntryResponse]
    users: list[UserResponse]
    integrations: list[
        PartialDiscordIntegrationResponse
        | PartialExternalConnectionIntegrationResponse
        | PartialGuildSubscriptionIntegrationResponse
    ]
    webhooks: list[
        ApplicationIncomingWebhookResponse
        | ChannelFollowerWebhookResponse
        | GuildIncomingWebhookResponse
    ]
    guild_scheduled_events: list[
        ExternalScheduledEventResponse
        | StageScheduledEventResponse
        | VoiceScheduledEventResponse
    ]
    threads: list[ThreadResponse]
    application_commands: list[ApplicationCommandResponse]
    auto_moderation_rules: list[
        DefaultKeywordRuleResponse
        | KeywordRuleResponse
        | MLSpamRuleResponse
        | MentionSpamRuleResponse
        | SpamLinkRuleResponse
        | None
    ]


class GuildBanResponse(BaseModel):
    user: UserResponse
    reason: str | None = None


class GuildChannelLocation(BaseModel):
    id: str
    kind: EmbeddedActivityLocationKind
    channel_id: SnowflakeType
    guild_id: SnowflakeType


class GuildChannelResponse(BaseModel):
    id: SnowflakeType
    type: ChannelTypes
    last_message_id: SnowflakeType | None = None
    flags: int
    last_pin_timestamp: datetime | None = None
    guild_id: SnowflakeType
    name: str
    parent_id: SnowflakeType | None = None
    rate_limit_per_user: int | None = None
    bitrate: int | None = None
    user_limit: int | None = None
    rtc_region: str | None = None
    video_quality_mode: VideoQualityModes | None = None
    permissions: str | None = None
    topic: str | None = None
    default_auto_archive_duration: ThreadAutoArchiveDuration | None = None
    default_thread_rate_limit_per_user: int | None = None
    position: int
    permission_overwrites: list[ChannelPermissionOverwriteResponse] | None = None
    nsfw: bool | None = None
    available_tags: list[ForumTagResponse] | None = None
    default_reaction_emoji: DefaultReactionEmojiResponse | None = None
    default_sort_order: ThreadSortOrder | None = None
    default_forum_layout: ForumLayout | None = None
    default_tag_setting: ThreadSearchTagSetting | None = None
    hd_streaming_until: datetime | None = None
    hd_streaming_buyer_id: SnowflakeType | None = None


class GuildCreateRequest(BaseModel):
    description: Annotated[str | None, Field(max_length=300, min_length=0)] = None
    name: Annotated[str, Field(max_length=100, min_length=2)]
    region: str | None = None
    icon: str | None = None
    verification_level: VerificationLevels | None = None
    default_message_notifications: UserNotificationSettings | None = None
    explicit_content_filter: GuildExplicitContentFilterTypes | None = None
    preferred_locale: AvailableLocalesEnum | None = None
    afk_timeout: AfkTimeouts | None = None
    roles: Annotated[
        list[CreateGuildRequestRoleItem] | None, Field(max_length=1521)
    ] = None
    channels: Annotated[
        list[CreateGuildRequestChannelItem] | None, Field(max_length=1521)
    ] = None
    afk_channel_id: SnowflakeType | None = None
    system_channel_id: SnowflakeType | None = None
    system_channel_flags: int | None = None


class GuildExplicitContentFilterTypes(RootModel[int]):
    root: int


class GuildFeatures(RootModel[str]):
    root: str


class GuildHomeSettingsResponse(BaseModel):
    guild_id: SnowflakeType
    enabled: bool
    welcome_message: WelcomeMessageResponse | None = None
    new_member_actions: list[NewMemberActionResponse | None] | None = None
    resource_channels: list[ResourceChannelResponse | None] | None = None


class GuildIncomingWebhookResponse(BaseModel):
    application_id: SnowflakeType | None = None
    avatar: str | None = None
    channel_id: SnowflakeType | None = None
    guild_id: SnowflakeType | None = None
    id: SnowflakeType
    name: str
    type: WebhookTypes
    user: UserResponse | None = None
    token: str | None = None
    url: AnyUrl | None = None


class GuildInviteResponse(BaseModel):
    type: InviteTypes | None = None
    code: str
    inviter: UserResponse | None = None
    max_age: int | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None
    is_contact: bool | None = None
    flags: int | None = None
    guild: InviteGuildResponse | None = None
    guild_id: SnowflakeType | None = None
    channel: InviteChannelResponse | None = None
    stage_instance: InviteStageInstanceResponse | None = None
    target_type: InviteTargetTypes | None = None
    target_user: UserResponse | None = None
    target_application: InviteApplicationResponse | None = None
    guild_scheduled_event: ScheduledEventResponse | None = None
    uses: int | None = None
    max_uses: int | None = None
    temporary: bool | None = None
    approximate_member_count: int | None = None
    approximate_presence_count: int | None = None
    is_nickname_changeable: bool | None = None


class GuildMFALevel(RootModel[int]):
    root: int


class GuildMFALevelResponse(BaseModel):
    level: GuildMFALevel


class GuildMemberResponse(BaseModel):
    avatar: str | None = None
    avatar_decoration_data: UserAvatarDecorationResponse | None = None
    banner: str | None = None
    communication_disabled_until: datetime | None = None
    flags: int
    joined_at: datetime
    nick: str | None = None
    pending: bool
    premium_since: datetime | None = None
    roles: list[SnowflakeType]
    user: UserResponse
    mute: bool
    deaf: bool


class GuildNSFWContentLevel(RootModel[int]):
    root: int


class GuildOnboardingMode(RootModel[int]):
    root: int


class GuildOnboardingResponse(BaseModel):
    guild_id: SnowflakeType
    prompts: list[OnboardingPromptResponse]
    default_channel_ids: list[SnowflakeType]
    enabled: bool


class GuildPatchRequestPartial(BaseModel):
    name: Annotated[str | None, Field(max_length=100, min_length=2)] = None
    description: Annotated[str | None, Field(max_length=300, min_length=0)] = None
    region: str | None = None
    icon: str | None = None
    verification_level: VerificationLevels | None = None
    default_message_notifications: UserNotificationSettings | None = None
    explicit_content_filter: GuildExplicitContentFilterTypes | None = None
    preferred_locale: AvailableLocalesEnum | None = None
    afk_timeout: AfkTimeouts | None = None
    afk_channel_id: SnowflakeType | None = None
    system_channel_id: SnowflakeType | None = None
    owner_id: SnowflakeType | None = None
    splash: str | None = None
    banner: str | None = None
    system_channel_flags: int | None = None
    features: Annotated[list[Feature | None] | None, Field(max_length=1521)] = None
    discovery_splash: str | None = None
    home_header: str | None = None
    rules_channel_id: SnowflakeType | None = None
    safety_alerts_channel_id: SnowflakeType | None = None
    public_updates_channel_id: SnowflakeType | None = None
    premium_progress_bar_enabled: bool | None = None


class GuildPreviewResponse(BaseModel):
    id: SnowflakeType
    name: str
    icon: str | None = None
    description: str | None = None
    home_header: str | None = None
    splash: str | None = None
    discovery_splash: str | None = None
    features: list[GuildFeatures]
    approximate_member_count: int
    approximate_presence_count: int
    emojis: list[EmojiResponse]
    stickers: list[GuildStickerResponse]


class GuildProductPurchaseResponse(BaseModel):
    listing_id: SnowflakeType
    product_name: str


class GuildPruneResponse(BaseModel):
    pruned: int | None = None


class GuildResponse(BaseModel):
    id: SnowflakeType
    name: str
    icon: str | None = None
    description: str | None = None
    home_header: str | None = None
    splash: str | None = None
    discovery_splash: str | None = None
    features: list[GuildFeatures]
    banner: str | None = None
    owner_id: SnowflakeType
    application_id: SnowflakeType | None = None
    region: str
    afk_channel_id: SnowflakeType | None = None
    afk_timeout: AfkTimeouts
    system_channel_id: SnowflakeType | None = None
    system_channel_flags: int
    widget_enabled: bool
    widget_channel_id: SnowflakeType | None = None
    verification_level: VerificationLevels
    roles: list[GuildRoleResponse]
    default_message_notifications: UserNotificationSettings
    mfa_level: GuildMFALevel
    explicit_content_filter: GuildExplicitContentFilterTypes
    max_presences: int | None = None
    max_members: int | None = None
    max_stage_video_channel_users: int | None = None
    max_video_channel_users: int | None = None
    vanity_url_code: str | None = None
    premium_tier: PremiumGuildTiers
    premium_subscription_count: int
    preferred_locale: AvailableLocalesEnum
    rules_channel_id: SnowflakeType | None = None
    safety_alerts_channel_id: SnowflakeType | None = None
    public_updates_channel_id: SnowflakeType | None = None
    premium_progress_bar_enabled: bool
    nsfw: bool
    nsfw_level: GuildNSFWContentLevel
    emojis: list[EmojiResponse]
    stickers: list[GuildStickerResponse]


class GuildRoleResponse(BaseModel):
    id: SnowflakeType
    name: str
    description: str | None = None
    permissions: str
    position: int
    color: int
    hoist: bool
    managed: bool
    mentionable: bool
    icon: str | None = None
    unicode_emoji: str | None = None
    tags: GuildRoleTagsResponse | None = None


class GuildRoleTagsResponse(BaseModel):
    premium_subscriber: None = None
    bot_id: SnowflakeType | None = None
    integration_id: SnowflakeType | None = None
    subscription_listing_id: SnowflakeType | None = None
    available_for_purchase: None = None
    guild_connections: None = None


class GuildScheduledEventEntityTypes(RootModel[int]):
    root: int


class GuildScheduledEventPrivacyLevels(RootModel[int]):
    root: int


class GuildScheduledEventStatuses(RootModel[int]):
    root: int


class GuildStickerResponse(BaseModel):
    id: SnowflakeType
    name: str
    tags: str
    type: StickerTypes
    format_type: StickerFormatTypes | None = None
    description: str | None = None
    available: bool
    guild_id: SnowflakeType
    user: UserResponse | None = None


class GuildSubscriptionIntegrationResponse(BaseModel):
    type: IntegrationTypes
    name: str | None = None
    account: AccountResponse | None = None
    enabled: bool | None = None
    id: SnowflakeType


class GuildTemplateChannelResponse(BaseModel):
    id: int | None = None
    type: ChannelTypes
    name: str | None = None
    position: int | None = None
    topic: str | None = None
    bitrate: int
    user_limit: int
    nsfw: bool
    rate_limit_per_user: int
    parent_id: SnowflakeType | None = None
    default_auto_archive_duration: ThreadAutoArchiveDuration | None = None
    permission_overwrites: list[ChannelPermissionOverwriteResponse | None]
    available_tags: list[GuildTemplateChannelTags] | None = None
    template: str
    default_reaction_emoji: DefaultReactionEmojiResponse | None = None
    default_thread_rate_limit_per_user: int | None = None
    default_sort_order: ThreadSortOrder | None = None
    default_forum_layout: ForumLayout | None = None
    default_tag_setting: ThreadSearchTagSetting | None = None
    icon_emoji: IconEmojiResponse | None = None
    theme_color: int | None = None


class GuildTemplateChannelTags(BaseModel):
    name: str
    emoji_id: SnowflakeType | None = None
    emoji_name: str | None = None
    moderated: bool | None = None


class GuildTemplateResponse(BaseModel):
    code: str
    name: str
    description: str | None = None
    usage_count: int
    creator_id: SnowflakeType
    creator: UserResponse | None = None
    created_at: datetime
    updated_at: datetime
    source_guild_id: SnowflakeType
    serialized_source_guild: GuildTemplateSnapshotResponse
    is_dirty: bool | None = None


class GuildTemplateRoleResponse(BaseModel):
    id: int
    name: str
    permissions: str
    color: int
    hoist: bool
    mentionable: bool
    icon: str | None = None
    unicode_emoji: str | None = None


class GuildTemplateSnapshotResponse(BaseModel):
    name: str
    description: str | None = None
    region: str | None = None
    verification_level: VerificationLevels
    default_message_notifications: UserNotificationSettings
    explicit_content_filter: GuildExplicitContentFilterTypes
    preferred_locale: AvailableLocalesEnum
    afk_channel_id: SnowflakeType | None = None
    afk_timeout: AfkTimeouts
    system_channel_id: SnowflakeType | None = None
    system_channel_flags: int
    roles: list[GuildTemplateRoleResponse]
    channels: list[GuildTemplateChannelResponse]


class GuildWelcomeChannel(BaseModel):
    channel_id: SnowflakeType
    description: Annotated[str, Field(max_length=50, min_length=1)]
    emoji_id: SnowflakeType | None = None
    emoji_name: Annotated[str | None, Field(max_length=152133)] = None


class GuildWelcomeScreenChannelResponse(BaseModel):
    channel_id: SnowflakeType
    description: str
    emoji_id: SnowflakeType | None = None
    emoji_name: str | None = None


class GuildWelcomeScreenResponse(BaseModel):
    description: str | None = None
    welcome_channels: list[GuildWelcomeScreenChannelResponse]


class GuildWithCountsResponse(BaseModel):
    id: SnowflakeType
    name: str
    icon: str | None = None
    description: str | None = None
    home_header: str | None = None
    splash: str | None = None
    discovery_splash: str | None = None
    features: list[GuildFeatures]
    banner: str | None = None
    owner_id: SnowflakeType
    application_id: SnowflakeType | None = None
    region: str
    afk_channel_id: SnowflakeType | None = None
    afk_timeout: AfkTimeouts
    system_channel_id: SnowflakeType | None = None
    system_channel_flags: int
    widget_enabled: bool
    widget_channel_id: SnowflakeType | None = None
    verification_level: VerificationLevels
    roles: list[GuildRoleResponse]
    default_message_notifications: UserNotificationSettings
    mfa_level: GuildMFALevel
    explicit_content_filter: GuildExplicitContentFilterTypes
    max_presences: int | None = None
    max_members: int | None = None
    max_stage_video_channel_users: int | None = None
    max_video_channel_users: int | None = None
    vanity_url_code: str | None = None
    premium_tier: PremiumGuildTiers
    premium_subscription_count: int
    preferred_locale: AvailableLocalesEnum
    rules_channel_id: SnowflakeType | None = None
    safety_alerts_channel_id: SnowflakeType | None = None
    public_updates_channel_id: SnowflakeType | None = None
    premium_progress_bar_enabled: bool
    nsfw: bool
    nsfw_level: GuildNSFWContentLevel
    emojis: list[EmojiResponse]
    stickers: list[GuildStickerResponse]
    approximate_member_count: int | None = None
    approximate_presence_count: int | None = None


class IconEmojiResponse(BaseModel):
    pass


class IncomingWebhookInteractionRequest(BaseModel):
    content: Annotated[str | None, Field(max_length=2000)] = None
    embeds: Annotated[list[RichEmbed] | None, Field(max_length=10)] = None
    allowed_mentions: MessageAllowedMentionsRequest | None = None
    components: Annotated[
        list[
            ActionRowComponentForMessageRequest
            | ContainerComponentForMessageRequest
            | FileComponentForMessageRequest
            | MediaGalleryComponentForMessageRequest
            | SectionComponentForMessageRequest
            | SeparatorComponentForMessageRequest
            | TextDisplayComponentForMessageRequest
        ]
        | None,
        Field(max_length=40),
    ] = None
    attachments: Annotated[
        list[MessageAttachmentRequest] | None, Field(max_length=10)
    ] = None
    poll: PollCreateRequest | None = None
    tts: bool | None = None
    flags: int | None = None


class IncomingWebhookRequestPartial(BaseModel):
    content: Annotated[str | None, Field(max_length=2000)] = None
    embeds: Annotated[list[RichEmbed] | None, Field(max_length=10)] = None
    allowed_mentions: MessageAllowedMentionsRequest | None = None
    components: Annotated[
        list[
            ActionRowComponentForMessageRequest
            | ContainerComponentForMessageRequest
            | FileComponentForMessageRequest
            | MediaGalleryComponentForMessageRequest
            | SectionComponentForMessageRequest
            | SeparatorComponentForMessageRequest
            | TextDisplayComponentForMessageRequest
        ]
        | None,
        Field(max_length=40),
    ] = None
    attachments: Annotated[
        list[MessageAttachmentRequest] | None, Field(max_length=10)
    ] = None
    poll: PollCreateRequest | None = None
    tts: bool | None = None
    flags: int | None = None
    username: Annotated[str | None, Field(max_length=80, min_length=1)] = None
    avatar_url: AnyUrl | None = None
    thread_name: Annotated[str | None, Field(max_length=100, min_length=0)] = None
    applied_tags: Annotated[list[SnowflakeType] | None, Field(max_length=5)] = None


class IncomingWebhookUpdateForInteractionCallbackRequestPartial(BaseModel):
    content: Annotated[str | None, Field(max_length=2000)] = None
    embeds: Annotated[list[RichEmbed] | None, Field(max_length=10)] = None
    allowed_mentions: MessageAllowedMentionsRequest | None = None
    components: Annotated[
        list[
            ActionRowComponentForMessageRequest
            | ContainerComponentForMessageRequest
            | FileComponentForMessageRequest
            | MediaGalleryComponentForMessageRequest
            | SectionComponentForMessageRequest
            | SeparatorComponentForMessageRequest
            | TextDisplayComponentForMessageRequest
        ]
        | None,
        Field(max_length=40),
    ] = None
    attachments: Annotated[
        list[MessageAttachmentRequest] | None, Field(max_length=10)
    ] = None
    flags: int | None = None


class IncomingWebhookUpdateRequestPartial(BaseModel):
    content: Annotated[str | None, Field(max_length=2000)] = None
    embeds: Annotated[list[RichEmbed] | None, Field(max_length=10)] = None
    allowed_mentions: MessageAllowedMentionsRequest | None = None
    components: Annotated[
        list[
            ActionRowComponentForMessageRequest
            | ContainerComponentForMessageRequest
            | FileComponentForMessageRequest
            | MediaGalleryComponentForMessageRequest
            | SectionComponentForMessageRequest
            | SeparatorComponentForMessageRequest
            | TextDisplayComponentForMessageRequest
        ]
        | None,
        Field(max_length=40),
    ] = None
    attachments: Annotated[
        list[MessageAttachmentRequest] | None, Field(max_length=10)
    ] = None
    poll: PollCreateRequest | None = None
    flags: int | None = None


class InnerErrors(BaseModel):
    model_config = ConfigDict(extra="forbid")
    field_errors: Annotated[list[Error], Field(alias="_errors")]
    """\n    The list of errors for this field\n"""


class Int53Type(RootModel[int]):
    root: Annotated[int, Field(ge=-9007199254740991, le=9007199254740991)]


class IntegrationApplicationResponse(BaseModel):
    id: SnowflakeType
    name: str
    icon: str | None = None
    description: str
    type: ApplicationTypes | None = None
    cover_image: str | None = None
    primary_sku_id: SnowflakeType | None = None
    bot: UserResponse | None = None


class IntegrationExpireBehaviorTypes(RootModel[int]):
    root: int


class IntegrationExpireGracePeriodTypes(RootModel[int]):
    root: int


class IntegrationTypes(RootModel[str]):
    root: str


class InteractionApplicationCommandAutocompleteCallbackIntegerData(BaseModel):
    choices: Annotated[
        list[ApplicationCommandOptionIntegerChoice | None] | None, Field(max_length=25)
    ] = None


class InteractionApplicationCommandAutocompleteCallbackNumberData(BaseModel):
    choices: Annotated[
        list[ApplicationCommandOptionNumberChoice | None] | None, Field(max_length=25)
    ] = None


class InteractionApplicationCommandAutocompleteCallbackStringData(BaseModel):
    choices: Annotated[
        list[ApplicationCommandOptionStringChoice | None] | None, Field(max_length=25)
    ] = None


class InteractionCallbackResponse(BaseModel):
    interaction: InteractionResponse
    resource: (
        CreateMessageInteractionCallbackResponse
        | LaunchActivityInteractionCallbackResponse
        | UpdateMessageInteractionCallbackResponse
        | None
    ) = None


class InteractionCallbackTypes(RootModel[int]):
    root: int


class InteractionContextType(RootModel[int]):
    root: int


class InteractionResponse(BaseModel):
    id: SnowflakeType
    type: InteractionTypes
    response_message_id: SnowflakeType | None = None
    response_message_loading: bool | None = None
    response_message_ephemeral: bool | None = None
    channel_id: SnowflakeType | None = None
    guild_id: SnowflakeType | None = None


class InteractionTypes(RootModel[int]):
    root: int


class InviteApplicationResponse(BaseModel):
    id: SnowflakeType
    name: str
    icon: str | None = None
    description: str
    type: ApplicationTypes | None = None
    cover_image: str | None = None
    primary_sku_id: SnowflakeType | None = None
    bot: UserResponse | None = None
    slug: str | None = None
    guild_id: SnowflakeType | None = None
    rpc_origins: list[str | None] | None = None
    bot_public: bool | None = None
    bot_require_code_grant: bool | None = None
    terms_of_service_url: AnyUrl | None = None
    privacy_policy_url: AnyUrl | None = None
    custom_install_url: AnyUrl | None = None
    install_params: ApplicationOAuth2InstallParamsResponse | None = None
    integration_types_config: dict[str, Any] | None = None
    verify_key: str
    flags: int
    max_participants: int | None = None
    tags: list[str] | None = None


class InviteChannelRecipientResponse(BaseModel):
    username: str


class InviteChannelResponse(BaseModel):
    id: SnowflakeType
    type: ChannelTypes
    name: str | None = None
    icon: str | None = None
    recipients: list[InviteChannelRecipientResponse] | None = None


class InviteGuildResponse(BaseModel):
    id: SnowflakeType
    name: str
    splash: str | None = None
    banner: str | None = None
    description: str | None = None
    icon: str | None = None
    features: list[GuildFeatures]
    verification_level: VerificationLevels | None = None
    vanity_url_code: str | None = None
    nsfw_level: GuildNSFWContentLevel | None = None
    nsfw: bool | None = None
    premium_subscription_count: int | None = None


class InviteStageInstanceResponse(BaseModel):
    topic: str
    participant_count: int | None = None
    speaker_count: int | None = None
    members: list[GuildMemberResponse] | None = None


class InviteTargetTypes(RootModel[int]):
    root: int


class InviteTypes(RootModel[int]):
    root: int


class KeywordFilterItem(RootModel[str]):
    root: Annotated[str, Field(max_length=60, min_length=1)]


class KeywordRuleResponse(BaseModel):
    id: SnowflakeType
    guild_id: SnowflakeType
    creator_id: SnowflakeType
    name: str
    event_type: AutomodEventType
    actions: list[
        BlockMessageActionResponse
        | FlagToChannelActionResponse
        | QuarantineUserActionResponse
        | UserCommunicationDisabledActionResponse
    ]
    trigger_type: AutomodTriggerType
    enabled: bool | None = None
    exempt_roles: list[SnowflakeType] | None = None
    exempt_channels: list[SnowflakeType] | None = None
    trigger_metadata: KeywordTriggerMetadataResponse


class KeywordTriggerMetadata(BaseModel):
    keyword_filter: Annotated[
        list[KeywordFilterItem] | None, Field(max_length=1000)
    ] = None
    regex_patterns: Annotated[list[RegexPattern] | None, Field(max_length=10)] = None
    allow_list: Annotated[list[AllowListItem] | None, Field(max_length=100)] = None


class KeywordTriggerMetadataResponse(BaseModel):
    keyword_filter: list[str]
    regex_patterns: list[str]
    allow_list: list[str]


class KeywordUpsertRequest(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    event_type: AutomodEventType
    actions: Annotated[
        list[
            BlockMessageAction
            | FlagToChannelAction
            | QuarantineUserAction
            | UserCommunicationDisabledAction
        ]
        | None,
        Field(max_length=5, min_length=1),
    ] = None
    enabled: bool | None = None
    exempt_roles: Annotated[list[SnowflakeType] | None, Field(max_length=20)] = None
    exempt_channels: Annotated[list[SnowflakeType] | None, Field(max_length=50)] = None
    trigger_type: AutomodTriggerType
    trigger_metadata: KeywordTriggerMetadata | None = None


class KeywordUpsertRequestPartial(BaseModel):
    name: Annotated[str | None, Field(max_length=100)] = None
    event_type: AutomodEventType | None = None
    actions: Annotated[
        list[
            BlockMessageAction
            | FlagToChannelAction
            | QuarantineUserAction
            | UserCommunicationDisabledAction
        ]
        | None,
        Field(max_length=5, min_length=1),
    ] = None
    enabled: bool | None = None
    exempt_roles: Annotated[list[SnowflakeType] | None, Field(max_length=20)] = None
    exempt_channels: Annotated[list[SnowflakeType] | None, Field(max_length=50)] = None
    trigger_type: AutomodTriggerType | None = None
    trigger_metadata: KeywordTriggerMetadata | None = None


class LaunchActivityInteractionCallbackRequest(BaseModel):
    type: InteractionCallbackTypes


class LaunchActivityInteractionCallbackResponse(BaseModel):
    type: InteractionCallbackTypes


class ListApplicationEmojisResponse(BaseModel):
    items: list[EmojiResponse]


class ListGuildSoundboardSoundsResponse(BaseModel):
    items: list[SoundboardSoundResponse]


class LobbyMemberRequest(BaseModel):
    id: SnowflakeType
    metadata: dict[str, Any] | None = None
    flags: Flags | None = None


class LobbyMemberResponse(BaseModel):
    id: SnowflakeType
    metadata: dict[str, Any] | None = None
    flags: int


class LobbyMessageResponse(BaseModel):
    id: SnowflakeType
    type: MessageType
    content: str
    lobby_id: SnowflakeType
    channel_id: SnowflakeType
    author: UserResponse
    metadata: dict[str, Any] | None = None
    flags: int
    application_id: SnowflakeType | None = None


class LobbyResponse(BaseModel):
    id: SnowflakeType
    application_id: SnowflakeType
    metadata: dict[str, Any] | None = None
    members: list[LobbyMemberResponse] | None = None
    linked_channel: GuildChannelResponse | None = None


class MLSpamRuleResponse(BaseModel):
    id: SnowflakeType
    guild_id: SnowflakeType
    creator_id: SnowflakeType
    name: str
    event_type: AutomodEventType
    actions: list[
        BlockMessageActionResponse
        | FlagToChannelActionResponse
        | QuarantineUserActionResponse
        | UserCommunicationDisabledActionResponse
    ]
    trigger_type: AutomodTriggerType
    enabled: bool | None = None
    exempt_roles: list[SnowflakeType] | None = None
    exempt_channels: list[SnowflakeType] | None = None
    trigger_metadata: MLSpamTriggerMetadataResponse


class MLSpamTriggerMetadata(BaseModel):
    pass


class MLSpamTriggerMetadataResponse(BaseModel):
    pass


class MLSpamUpsertRequest(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    event_type: AutomodEventType
    actions: Annotated[
        list[
            BlockMessageAction
            | FlagToChannelAction
            | QuarantineUserAction
            | UserCommunicationDisabledAction
        ]
        | None,
        Field(max_length=5, min_length=1),
    ] = None
    enabled: bool | None = None
    exempt_roles: Annotated[list[SnowflakeType] | None, Field(max_length=20)] = None
    exempt_channels: Annotated[list[SnowflakeType] | None, Field(max_length=50)] = None
    trigger_type: AutomodTriggerType
    trigger_metadata: MLSpamTriggerMetadata | None = None


class MLSpamUpsertRequestPartial(BaseModel):
    name: Annotated[str | None, Field(max_length=100)] = None
    event_type: AutomodEventType | None = None
    actions: Annotated[
        list[
            BlockMessageAction
            | FlagToChannelAction
            | QuarantineUserAction
            | UserCommunicationDisabledAction
        ]
        | None,
        Field(max_length=5, min_length=1),
    ] = None
    enabled: bool | None = None
    exempt_roles: Annotated[list[SnowflakeType] | None, Field(max_length=20)] = None
    exempt_channels: Annotated[list[SnowflakeType] | None, Field(max_length=50)] = None
    trigger_type: AutomodTriggerType | None = None
    trigger_metadata: MLSpamTriggerMetadata | None = None


class MediaGalleryComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    items: Annotated[list[MediaGalleryItemRequest], Field(max_length=10, min_length=1)]


class MediaGalleryComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    items: list[MediaGalleryItemResponse]


class MediaGalleryItemRequest(BaseModel):
    description: Annotated[str | None, Field(max_length=1024, min_length=1)] = None
    spoiler: bool | None = None
    media: UnfurledMediaRequest


class MediaGalleryItemResponse(BaseModel):
    media: UnfurledMediaResponse
    description: str | None = None
    spoiler: bool


class MentionSpamRuleResponse(BaseModel):
    id: SnowflakeType
    guild_id: SnowflakeType
    creator_id: SnowflakeType
    name: str
    event_type: AutomodEventType
    actions: list[
        BlockMessageActionResponse
        | FlagToChannelActionResponse
        | QuarantineUserActionResponse
        | UserCommunicationDisabledActionResponse
    ]
    trigger_type: AutomodTriggerType
    enabled: bool | None = None
    exempt_roles: list[SnowflakeType] | None = None
    exempt_channels: list[SnowflakeType] | None = None
    trigger_metadata: MentionSpamTriggerMetadataResponse


class MentionSpamTriggerMetadata(BaseModel):
    mention_total_limit: Annotated[int, Field(ge=0, le=50)]
    mention_raid_protection_enabled: bool | None = None


class MentionSpamTriggerMetadataResponse(BaseModel):
    mention_total_limit: int
    mention_raid_protection_enabled: bool | None = None


class MentionSpamUpsertRequest(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    event_type: AutomodEventType
    actions: Annotated[
        list[
            BlockMessageAction
            | FlagToChannelAction
            | QuarantineUserAction
            | UserCommunicationDisabledAction
        ]
        | None,
        Field(max_length=5, min_length=1),
    ] = None
    enabled: bool | None = None
    exempt_roles: Annotated[list[SnowflakeType] | None, Field(max_length=20)] = None
    exempt_channels: Annotated[list[SnowflakeType] | None, Field(max_length=50)] = None
    trigger_type: AutomodTriggerType
    trigger_metadata: MentionSpamTriggerMetadata | None = None


class MentionSpamUpsertRequestPartial(BaseModel):
    name: Annotated[str | None, Field(max_length=100)] = None
    event_type: AutomodEventType | None = None
    actions: Annotated[
        list[
            BlockMessageAction
            | FlagToChannelAction
            | QuarantineUserAction
            | UserCommunicationDisabledAction
        ]
        | None,
        Field(max_length=5, min_length=1),
    ] = None
    enabled: bool | None = None
    exempt_roles: Annotated[list[SnowflakeType] | None, Field(max_length=20)] = None
    exempt_channels: Annotated[list[SnowflakeType] | None, Field(max_length=50)] = None
    trigger_type: AutomodTriggerType | None = None
    trigger_metadata: MentionSpamTriggerMetadata | None = None


class MentionableSelectComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    custom_id: Annotated[str, Field(max_length=100)]
    placeholder: Annotated[str | None, Field(max_length=150)] = None
    min_values: Annotated[int | None, Field(ge=0, le=25)] = None
    max_values: Annotated[int | None, Field(ge=1, le=25)] = None
    disabled: bool | None = None
    default_values: Annotated[
        list[RoleSelectDefaultValue | UserSelectDefaultValue] | None,
        Field(max_length=25),
    ] = None


class MentionableSelectComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    custom_id: str
    placeholder: str | None = None
    min_values: int | None = None
    max_values: int | None = None
    disabled: bool | None = None
    default_values: (
        list[RoleSelectDefaultValueResponse | UserSelectDefaultValueResponse] | None
    ) = None


class MessageActivityResponse(BaseModel):
    pass


class MessageAllowedMentionsRequest(BaseModel):
    parse: Annotated[
        list[AllowedMentionTypes | None] | None, Field(max_length=1521)
    ] = None
    users: Annotated[list[SnowflakeType | None] | None, Field(max_length=100)] = None
    roles: Annotated[list[SnowflakeType | None] | None, Field(max_length=100)] = None
    replied_user: bool | None = None


class MessageAttachmentRequest(BaseModel):
    id: SnowflakeType
    filename: Annotated[str | None, Field(max_length=1024)] = None
    description: Annotated[str | None, Field(max_length=1024)] = None
    duration_secs: Annotated[float | None, Field(ge=0.0, le=2147483647.0)] = None
    waveform: Annotated[str | None, Field(max_length=400)] = None
    title: Annotated[str | None, Field(max_length=1024)] = None
    is_remix: bool | None = None


class MessageAttachmentResponse(BaseModel):
    id: SnowflakeType
    filename: str
    size: int
    url: AnyUrl
    proxy_url: AnyUrl
    width: int | None = None
    height: int | None = None
    duration_secs: float | None = None
    waveform: str | None = None
    description: str | None = None
    content_type: str | None = None
    ephemeral: bool | None = None
    title: str | None = None
    application: ApplicationResponse | None = None
    clip_created_at: datetime | None = None
    clip_participants: list[UserResponse] | None = None


class MessageCallResponse(BaseModel):
    ended_timestamp: datetime | None = None
    participants: list[SnowflakeType]


class MessageComponentInteractionMetadataResponse(BaseModel):
    id: SnowflakeType
    type: InteractionTypes
    user: UserResponse | None = None
    authorizing_integration_owners: dict[str, SnowflakeType]
    original_response_message_id: SnowflakeType | None = None
    interacted_message_id: SnowflakeType


class MessageComponentSeparatorSpacingSize(RootModel[int]):
    root: int


class MessageComponentTypes(RootModel[int]):
    root: int


class MessageCreateRequest(BaseModel):
    content: Annotated[str | None, Field(max_length=4000)] = None
    embeds: Annotated[list[RichEmbed] | None, Field(max_length=10)] = None
    allowed_mentions: MessageAllowedMentionsRequest | None = None
    sticker_ids: Annotated[list[SnowflakeType] | None, Field(max_length=3)] = None
    components: Annotated[
        list[
            ActionRowComponentForMessageRequest
            | ContainerComponentForMessageRequest
            | FileComponentForMessageRequest
            | MediaGalleryComponentForMessageRequest
            | SectionComponentForMessageRequest
            | SeparatorComponentForMessageRequest
            | TextDisplayComponentForMessageRequest
        ]
        | None,
        Field(max_length=40),
    ] = None
    flags: int | None = None
    attachments: Annotated[
        list[MessageAttachmentRequest] | None, Field(max_length=10)
    ] = None
    poll: PollCreateRequest | None = None
    confetti_potion: ConfettiPotionCreateRequest | None = None
    message_reference: MessageReferenceRequest | None = None
    nonce: Nonce2 | Nonce3 | None = None
    enforce_nonce: bool | None = None
    tts: bool | None = None


class MessageEditRequestPartial(BaseModel):
    content: Annotated[str | None, Field(max_length=4000)] = None
    embeds: Annotated[list[RichEmbed] | None, Field(max_length=10)] = None
    flags: int | None = None
    allowed_mentions: MessageAllowedMentionsRequest | None = None
    sticker_ids: Annotated[list[SnowflakeType] | None, Field(max_length=1521)] = None
    components: Annotated[
        list[
            ActionRowComponentForMessageRequest
            | ContainerComponentForMessageRequest
            | FileComponentForMessageRequest
            | MediaGalleryComponentForMessageRequest
            | SectionComponentForMessageRequest
            | SeparatorComponentForMessageRequest
            | TextDisplayComponentForMessageRequest
        ]
        | None,
        Field(max_length=40),
    ] = None
    attachments: Annotated[
        list[MessageAttachmentRequest] | None, Field(max_length=10)
    ] = None


class MessageEmbedAuthorResponse(BaseModel):
    name: str
    url: str | None = None
    icon_url: str | None = None
    proxy_icon_url: AnyUrl | None = None


class MessageEmbedFieldResponse(BaseModel):
    name: str
    value: str
    inline: bool


class MessageEmbedFooterResponse(BaseModel):
    text: str
    icon_url: str | None = None
    proxy_icon_url: AnyUrl | None = None


class MessageEmbedImageResponse(BaseModel):
    url: str | None = None
    proxy_url: AnyUrl | None = None
    width: UInt32Type | None = None
    height: UInt32Type | None = None
    placeholder: str | None = None
    placeholder_version: UInt32Type | None = None
    description: str | None = None
    flags: UInt32Type | None = None


class MessageEmbedProviderResponse(BaseModel):
    name: str
    url: AnyUrl | None = None


class MessageEmbedResponse(BaseModel):
    type: str
    url: AnyUrl | None = None
    title: str | None = None
    description: str | None = None
    color: int | None = None
    timestamp: datetime | None = None
    fields: list[MessageEmbedFieldResponse] | None = None
    author: MessageEmbedAuthorResponse | None = None
    provider: MessageEmbedProviderResponse | None = None
    image: MessageEmbedImageResponse | None = None
    thumbnail: MessageEmbedImageResponse | None = None
    video: MessageEmbedVideoResponse | None = None
    footer: MessageEmbedFooterResponse | None = None


class MessageEmbedVideoResponse(BaseModel):
    url: str | None = None
    proxy_url: AnyUrl | None = None
    width: UInt32Type | None = None
    height: UInt32Type | None = None
    placeholder: str | None = None
    placeholder_version: UInt32Type | None = None
    description: str | None = None
    flags: UInt32Type | None = None


class MessageInteractionResponse(BaseModel):
    id: SnowflakeType
    type: InteractionTypes
    name: str
    user: UserResponse | None = None
    name_localized: str | None = None


class MessageMentionChannelResponse(BaseModel):
    id: SnowflakeType
    name: str
    type: ChannelTypes
    guild_id: SnowflakeType


class MessageReactionCountDetailsResponse(BaseModel):
    burst: int
    normal: int


class MessageReactionEmojiResponse(BaseModel):
    id: SnowflakeType | None = None
    name: str | None = None
    animated: bool | None = None


class MessageReactionResponse(BaseModel):
    emoji: MessageReactionEmojiResponse
    count: int
    count_details: MessageReactionCountDetailsResponse
    burst_colors: list[str]
    me_burst: bool
    me: bool


class MessageReferenceRequest(BaseModel):
    guild_id: SnowflakeType | None = None
    channel_id: SnowflakeType | None = None
    message_id: SnowflakeType
    fail_if_not_exists: bool | None = None
    type: MessageReferenceType | None = None


class MessageReferenceResponse(BaseModel):
    type: MessageReferenceType | None = None
    channel_id: SnowflakeType
    message_id: SnowflakeType | None = None
    guild_id: SnowflakeType | None = None


class MessageReferenceType(RootModel[int]):
    root: int


class MessageResponse(BaseModel):
    type: MessageType
    content: str
    mentions: list[UserResponse]
    mention_roles: list[SnowflakeType]
    attachments: list[MessageAttachmentResponse]
    embeds: list[MessageEmbedResponse]
    timestamp: datetime
    edited_timestamp: datetime | None = None
    flags: int
    components: list[
        ActionRowComponentResponse
        | ContainerComponentResponse
        | FileComponentResponse
        | MediaGalleryComponentResponse
        | SectionComponentResponse
        | SeparatorComponentResponse
        | TextDisplayComponentResponse
    ]
    resolved: ResolvedObjectsResponse | None = None
    stickers: list[GuildStickerResponse | StandardStickerResponse] | None = None
    sticker_items: list[MessageStickerItemResponse] | None = None
    id: SnowflakeType
    channel_id: SnowflakeType
    author: UserResponse
    pinned: bool
    mention_everyone: bool
    tts: bool
    call: MessageCallResponse | None = None
    activity: MessageActivityResponse | None = None
    application: BasicApplicationResponse | None = None
    application_id: SnowflakeType | None = None
    interaction: MessageInteractionResponse | None = None
    nonce: Nonce4 | Nonce5 | None = None
    webhook_id: SnowflakeType | None = None
    message_reference: MessageReferenceResponse | None = None
    thread: ThreadResponse | None = None
    mention_channels: list[MessageMentionChannelResponse | None] | None = None
    role_subscription_data: MessageRoleSubscriptionDataResponse | None = None
    purchase_notification: PurchaseNotificationResponse | None = None
    position: int | None = None
    poll: PollResponse | None = None
    interaction_metadata: (
        ApplicationCommandInteractionMetadataResponse
        | MessageComponentInteractionMetadataResponse
        | ModalSubmitInteractionMetadataResponse
        | None
    ) = None
    message_snapshots: list[MessageSnapshotResponse] | None = None
    reactions: list[MessageReactionResponse] | None = None
    referenced_message: BasicMessageResponse | None = None


class MessageRoleSubscriptionDataResponse(BaseModel):
    role_subscription_listing_id: SnowflakeType
    tier_name: str
    total_months_subscribed: int
    is_renewal: bool


class MessageSnapshotResponse(BaseModel):
    message: MinimalContentMessageResponse | None = None


class MessageStickerItemResponse(BaseModel):
    id: SnowflakeType
    name: str
    format_type: StickerFormatTypes


class MessageType(RootModel[int]):
    root: int


class MetadataItemTypes(RootModel[int]):
    root: int


class MinimalContentMessageResponse(BaseModel):
    type: MessageType
    content: str
    mentions: list[UserResponse]
    mention_roles: list[SnowflakeType]
    attachments: list[MessageAttachmentResponse]
    embeds: list[MessageEmbedResponse]
    timestamp: datetime
    edited_timestamp: datetime | None = None
    flags: int
    components: list[
        ActionRowComponentResponse
        | ContainerComponentResponse
        | FileComponentResponse
        | MediaGalleryComponentResponse
        | SectionComponentResponse
        | SeparatorComponentResponse
        | TextDisplayComponentResponse
    ]
    resolved: ResolvedObjectsResponse | None = None
    stickers: list[GuildStickerResponse | StandardStickerResponse] | None = None
    sticker_items: list[MessageStickerItemResponse] | None = None


class ModalInteractionCallbackRequest(BaseModel):
    type: InteractionCallbackTypes
    data: ModalInteractionCallbackRequestData


class ModalInteractionCallbackRequestData(BaseModel):
    custom_id: Annotated[str, Field(max_length=100)]
    title: Annotated[str, Field(max_length=45)]
    components: Annotated[
        list[ActionRowComponentForModalRequest], Field(max_length=40, min_length=1)
    ]


class ModalSubmitInteractionMetadataResponse(BaseModel):
    id: SnowflakeType
    type: InteractionTypes
    user: UserResponse | None = None
    authorizing_integration_owners: dict[str, SnowflakeType]
    original_response_message_id: SnowflakeType | None = None
    triggering_interaction_metadata: (
        ApplicationCommandInteractionMetadataResponse
        | MessageComponentInteractionMetadataResponse
    )


class MyGuildResponse(BaseModel):
    id: SnowflakeType
    name: str
    icon: str | None = None
    banner: str | None = None
    owner: bool
    permissions: str
    features: list[GuildFeatures]
    approximate_member_count: int | None = None
    approximate_presence_count: int | None = None


class NameplatePalette(RootModel[str]):
    root: str


class NewMemberActionResponse(BaseModel):
    channel_id: SnowflakeType
    action_type: NewMemberActionType
    title: str
    description: str
    emoji: SettingsEmojiResponse | None = None
    icon: str | None = None


class NewMemberActionType(RootModel[int]):
    root: int


class Nonce(RootModel[int]):
    root: Annotated[int, Field(ge=-9223372036854775808, le=9223372036854775807)]


class Nonce1(RootModel[str]):
    root: Annotated[str, Field(max_length=25)]


class Nonce2(RootModel[int]):
    root: Annotated[int, Field(ge=-9223372036854775808, le=9223372036854775807)]


class Nonce3(RootModel[str]):
    root: Annotated[str, Field(max_length=25)]


class Nonce4(RootModel[int]):
    root: Annotated[int, Field(ge=-9223372036854775808, le=9223372036854775807)]


class Nonce5(RootModel[str]):
    root: Annotated[str, Field(max_length=25)]


class Nonce6(RootModel[int]):
    root: Annotated[int, Field(ge=-9223372036854775808, le=9223372036854775807)]


class Nonce7(RootModel[str]):
    root: Annotated[str, Field(max_length=25)]


class OAuth2GetAuthorizationResponse(BaseModel):
    application: ApplicationResponse
    expires: datetime
    scopes: list[OAuth2Scopes]
    user: UserResponse | None = None


class OAuth2GetKeys(BaseModel):
    keys: list[OAuth2Key]


class OAuth2GetOpenIDConnectUserInfoResponse(BaseModel):
    sub: str
    email: str | None = None
    email_verified: bool | None = None
    preferred_username: str | None = None
    nickname: str | None = None
    picture: str | None = None
    locale: str | None = None


class OAuth2Key(BaseModel):
    kty: str
    use: str
    kid: str
    n: str
    e: str
    alg: str


class OAuth2Scopes(RootModel[str]):
    root: str


class OnboardingPromptOptionRequest(BaseModel):
    id: SnowflakeType | None = None
    title: Annotated[str, Field(max_length=50, min_length=1)]
    description: Annotated[str | None, Field(max_length=100)] = None
    emoji_id: SnowflakeType | None = None
    emoji_name: Annotated[str | None, Field(max_length=100)] = None
    emoji_animated: bool | None = None
    role_ids: Annotated[list[SnowflakeType] | None, Field(max_length=50)] = None
    channel_ids: Annotated[list[SnowflakeType] | None, Field(max_length=50)] = None


class OnboardingPromptOptionResponse(BaseModel):
    id: SnowflakeType
    title: str
    description: str
    emoji: SettingsEmojiResponse
    role_ids: list[SnowflakeType]
    channel_ids: list[SnowflakeType]


class OnboardingPromptResponse(BaseModel):
    id: SnowflakeType
    title: str
    options: list[OnboardingPromptOptionResponse]
    single_select: bool
    required: bool
    in_onboarding: bool
    type: OnboardingPromptType


class OnboardingPromptType(RootModel[int]):
    root: int


class PartialDiscordIntegrationResponse(BaseModel):
    id: SnowflakeType
    type: IntegrationTypes
    name: str | None = None
    account: AccountResponse | None = None
    application_id: SnowflakeType


class PartialExternalConnectionIntegrationResponse(BaseModel):
    id: SnowflakeType
    type: IntegrationTypes
    name: str | None = None
    account: AccountResponse | None = None


class PartialGuildSubscriptionIntegrationResponse(BaseModel):
    id: SnowflakeType
    type: IntegrationTypes
    name: str | None = None
    account: AccountResponse | None = None


class PollAnswerCreateRequest(BaseModel):
    poll_media: PollMediaCreateRequest


class PollAnswerDetailsResponse(BaseModel):
    users: list[UserResponse] | None = None


class PollAnswerResponse(BaseModel):
    answer_id: int
    poll_media: PollMediaResponse


class PollCreateRequest(BaseModel):
    question: PollMedia
    answers: Annotated[
        list[PollAnswerCreateRequest], Field(max_length=10, min_length=1)
    ]
    allow_multiselect: bool | None = None
    layout_type: PollLayoutTypes | None = None
    duration: Annotated[int | None, Field(ge=1, le=768)] = None


class PollEmoji(BaseModel):
    id: SnowflakeType | None = None
    name: Annotated[str | None, Field(max_length=32)] = None
    animated: bool | None = None


class PollEmojiCreateRequest(BaseModel):
    id: SnowflakeType | None = None
    name: Annotated[str | None, Field(max_length=32)] = None
    animated: bool | None = None


class PollLayoutTypes(RootModel[int]):
    root: int


class PollMedia(BaseModel):
    text: Annotated[str | None, Field(max_length=300, min_length=1)] = None
    emoji: PollEmoji | None = None


class PollMediaCreateRequest(BaseModel):
    text: Annotated[str | None, Field(max_length=300, min_length=1)] = None
    emoji: PollEmojiCreateRequest | None = None


class PollMediaResponse(BaseModel):
    text: str | None = None
    emoji: MessageReactionEmojiResponse | None = None


class PollResponse(BaseModel):
    question: PollMediaResponse
    answers: list[PollAnswerResponse]
    expiry: datetime
    allow_multiselect: bool
    layout_type: PollLayoutTypes
    results: PollResultsResponse


class PollResultsEntryResponse(BaseModel):
    id: int
    count: int
    me_voted: bool | None = None


class PollResultsResponse(BaseModel):
    answer_counts: list[PollResultsEntryResponse] | None = None
    is_finalized: bool


class PongInteractionCallbackRequest(BaseModel):
    type: InteractionCallbackTypes


class PremiumGuildTiers(RootModel[int]):
    root: int


class PremiumTypes(RootModel[int]):
    root: int


class PrivateApplicationResponse(BaseModel):
    id: SnowflakeType
    name: str
    icon: str | None = None
    description: str
    type: ApplicationTypes | None = None
    cover_image: str | None = None
    primary_sku_id: SnowflakeType | None = None
    bot: UserResponse | None = None
    slug: str | None = None
    guild_id: SnowflakeType | None = None
    rpc_origins: list[str | None] | None = None
    bot_public: bool | None = None
    bot_require_code_grant: bool | None = None
    terms_of_service_url: AnyUrl | None = None
    privacy_policy_url: AnyUrl | None = None
    custom_install_url: AnyUrl | None = None
    install_params: ApplicationOAuth2InstallParamsResponse | None = None
    integration_types_config: dict[str, Any] | None = None
    verify_key: str
    flags: int
    max_participants: int | None = None
    tags: list[str] | None = None
    redirect_uris: list[AnyUrl | None]
    interactions_endpoint_url: AnyUrl | None = None
    role_connections_verification_url: AnyUrl | None = None
    owner: UserResponse
    approximate_guild_count: int | None = None
    approximate_user_install_count: int
    explicit_content_filter: ApplicationExplicitContentFilterTypes
    team: TeamResponse | None = None


class PrivateChannelLocation(BaseModel):
    id: str
    kind: EmbeddedActivityLocationKind
    channel_id: SnowflakeType


class PrivateChannelResponse(BaseModel):
    id: SnowflakeType
    type: ChannelTypes
    last_message_id: SnowflakeType | None = None
    flags: int
    last_pin_timestamp: datetime | None = None
    recipients: list[UserResponse]


class PrivateGroupChannelResponse(BaseModel):
    id: SnowflakeType
    type: ChannelTypes
    last_message_id: SnowflakeType | None = None
    flags: int
    last_pin_timestamp: datetime | None = None
    recipients: list[UserResponse]
    name: str | None = None
    icon: str | None = None
    owner_id: SnowflakeType | None = None
    managed: bool | None = None
    application_id: SnowflakeType | None = None


class PrivateGuildMemberResponse(BaseModel):
    avatar: str | None = None
    avatar_decoration_data: UserAvatarDecorationResponse | None = None
    banner: str | None = None
    communication_disabled_until: datetime | None = None
    flags: int
    joined_at: datetime
    nick: str | None = None
    pending: bool
    premium_since: datetime | None = None
    roles: list[SnowflakeType]
    user: UserResponse
    mute: bool
    deaf: bool


class ProvisionalTokenResponse(BaseModel):
    token_type: str
    access_token: str
    expires_in: int
    scope: str
    id_token: str
    refresh_token: str | None = None
    scopes: list[str] | None = None
    expires_at_s: int | None = None


class PurchaseNotificationResponse(BaseModel):
    type: PurchaseType
    guild_product_purchase: GuildProductPurchaseResponse | None = None


class PurchaseType(RootModel[int]):
    root: int


class QuarantineUserAction(BaseModel):
    type: AutomodActionType
    metadata: QuarantineUserActionMetadata | None = None


class QuarantineUserActionMetadata(BaseModel):
    pass


class QuarantineUserActionMetadataResponse(BaseModel):
    pass


class QuarantineUserActionResponse(BaseModel):
    type: AutomodActionType
    metadata: QuarantineUserActionMetadataResponse


class ReactionTypes(RootModel[int]):
    root: int


class RegexPattern(RootModel[str]):
    root: Annotated[str, Field(max_length=260, min_length=1)]


class ResolvedObjectsResponse(BaseModel):
    users: dict[str, UserResponse]
    members: dict[str, GuildMemberResponse]
    channels: dict[
        str,
        GuildChannelResponse
        | PrivateChannelResponse
        | PrivateGroupChannelResponse
        | ThreadResponse,
    ]
    roles: dict[str, GuildRoleResponse]


class ResourceChannelResponse(BaseModel):
    channel_id: SnowflakeType
    title: str
    emoji: SettingsEmojiResponse | None = None
    icon: str | None = None
    description: str


class RichEmbed(BaseModel):
    type: Annotated[str | None, Field(max_length=152133)] = None
    url: AnyUrl | None = None
    title: Annotated[str | None, Field(max_length=256)] = None
    color: Annotated[int | None, Field(ge=0, le=16777215)] = None
    timestamp: datetime | None = None
    description: Annotated[str | None, Field(max_length=4096)] = None
    author: RichEmbedAuthor | None = None
    image: RichEmbedImage | None = None
    thumbnail: RichEmbedThumbnail | None = None
    footer: RichEmbedFooter | None = None
    fields: Annotated[list[RichEmbedField] | None, Field(max_length=25)] = None
    provider: RichEmbedProvider | None = None
    video: RichEmbedVideo | None = None


class RichEmbedAuthor(BaseModel):
    name: Annotated[str | None, Field(max_length=256)] = None
    url: AnyUrl | None = None
    icon_url: AnyUrl | None = None


class RichEmbedField(BaseModel):
    name: Annotated[str, Field(max_length=256)]
    value: Annotated[str, Field(max_length=1024)]
    inline: bool | None = None


class RichEmbedFooter(BaseModel):
    text: Annotated[str | None, Field(max_length=2048)] = None
    icon_url: AnyUrl | None = None


class RichEmbedImage(BaseModel):
    url: AnyUrl | None = None
    width: int | None = None
    height: int | None = None
    placeholder: Annotated[str | None, Field(max_length=64)] = None
    placeholder_version: Annotated[int | None, Field(ge=0, le=2147483647)] = None
    is_animated: bool | None = None
    description: Annotated[str | None, Field(max_length=4096)] = None


class RichEmbedProvider(BaseModel):
    name: Annotated[str | None, Field(max_length=256)] = None
    url: AnyUrl | None = None


class RichEmbedThumbnail(BaseModel):
    url: AnyUrl | None = None
    width: int | None = None
    height: int | None = None
    placeholder: Annotated[str | None, Field(max_length=64)] = None
    placeholder_version: Annotated[int | None, Field(ge=0, le=2147483647)] = None
    is_animated: bool | None = None
    description: Annotated[str | None, Field(max_length=4096)] = None


class RichEmbedVideo(BaseModel):
    url: AnyUrl | None = None
    width: int | None = None
    height: int | None = None
    placeholder: Annotated[str | None, Field(max_length=64)] = None
    placeholder_version: Annotated[int | None, Field(ge=0, le=2147483647)] = None
    is_animated: bool | None = None
    description: Annotated[str | None, Field(max_length=4096)] = None


class RoleSelectComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    custom_id: Annotated[str, Field(max_length=100)]
    placeholder: Annotated[str | None, Field(max_length=150)] = None
    min_values: Annotated[int | None, Field(ge=0, le=25)] = None
    max_values: Annotated[int | None, Field(ge=1, le=25)] = None
    disabled: bool | None = None
    default_values: Annotated[
        list[RoleSelectDefaultValue] | None, Field(max_length=25)
    ] = None


class RoleSelectComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    custom_id: str
    placeholder: str | None = None
    min_values: int | None = None
    max_values: int | None = None
    disabled: bool | None = None
    default_values: list[RoleSelectDefaultValueResponse] | None = None


class RoleSelectDefaultValue(BaseModel):
    type: SnowflakeSelectDefaultValueTypes
    id: SnowflakeType


class RoleSelectDefaultValueResponse(BaseModel):
    type: SnowflakeSelectDefaultValueTypes
    id: SnowflakeType


class SDKMessageRequest(BaseModel):
    content: Annotated[str | None, Field(max_length=4000)] = None
    embeds: Annotated[list[RichEmbed] | None, Field(max_length=10)] = None
    allowed_mentions: MessageAllowedMentionsRequest | None = None
    sticker_ids: Annotated[list[SnowflakeType] | None, Field(max_length=3)] = None
    components: Annotated[
        list[
            ActionRowComponentForMessageRequest
            | ContainerComponentForMessageRequest
            | FileComponentForMessageRequest
            | MediaGalleryComponentForMessageRequest
            | SectionComponentForMessageRequest
            | SeparatorComponentForMessageRequest
            | TextDisplayComponentForMessageRequest
        ]
        | None,
        Field(max_length=40),
    ] = None
    flags: int | None = None
    attachments: Annotated[
        list[MessageAttachmentRequest] | None, Field(max_length=10)
    ] = None
    poll: PollCreateRequest | None = None
    confetti_potion: ConfettiPotionCreateRequest | None = None
    message_reference: MessageReferenceRequest | None = None
    nonce: Nonce6 | Nonce7 | None = None
    enforce_nonce: bool | None = None
    tts: bool | None = None


class ScheduledEventResponse(BaseModel):
    id: SnowflakeType
    guild_id: SnowflakeType
    name: str
    description: str | None = None
    channel_id: SnowflakeType | None = None
    creator_id: SnowflakeType | None = None
    creator: UserResponse | None = None
    image: str | None = None
    scheduled_start_time: datetime
    scheduled_end_time: datetime | None = None
    status: GuildScheduledEventStatuses
    entity_type: GuildScheduledEventEntityTypes
    entity_id: SnowflakeType | None = None
    user_count: int | None = None
    privacy_level: GuildScheduledEventPrivacyLevels
    user_rsvp: ScheduledEventUserResponse | None = None


class ScheduledEventUserResponse(BaseModel):
    guild_scheduled_event_id: SnowflakeType
    user_id: SnowflakeType
    user: UserResponse | None = None
    member: GuildMemberResponse | None = None


class SectionComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    components: Annotated[
        list[TextDisplayComponentForMessageRequest], Field(max_length=3, min_length=1)
    ]
    accessory: ButtonComponentForMessageRequest | ThumbnailComponentForMessageRequest


class SectionComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    components: list[TextDisplayComponentResponse]
    accessory: ButtonComponentResponse | ThumbnailComponentResponse


class SeparatorComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    spacing: MessageComponentSeparatorSpacingSize | None = None
    divider: bool | None = None


class SeparatorComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    spacing: MessageComponentSeparatorSpacingSize
    divider: bool


class SettingsEmojiResponse(BaseModel):
    id: SnowflakeType | None = None
    name: str | None = None
    animated: bool | None = None


class SlackWebhook(BaseModel):
    text: Annotated[str | None, Field(max_length=2000)] = None
    username: Annotated[str | None, Field(max_length=152133)] = None
    icon_url: AnyUrl | None = None
    attachments: Annotated[list[WebhookSlackEmbed] | None, Field(max_length=1521)] = (
        None
    )


class SnowflakeSelectDefaultValueTypes(RootModel[str]):
    root: str


class SnowflakeType(RootModel[str]):
    root: Annotated[str, Field(pattern="^(0|[1-9][0-9]*)$")]


class SortingOrder(RootModel[str]):
    root: str


class SoundboardCreateRequest(BaseModel):
    name: Annotated[str, Field(max_length=32, min_length=2)]
    volume: Annotated[float | None, Field(ge=0.0, le=1.0)] = None
    emoji_id: SnowflakeType | None = None
    emoji_name: Annotated[str | None, Field(max_length=32, min_length=1)] = None
    sound: str


class SoundboardPatchRequestPartial(BaseModel):
    name: Annotated[str | None, Field(max_length=32, min_length=2)] = None
    volume: Annotated[float | None, Field(ge=0.0, le=1.0)] = None
    emoji_id: SnowflakeType | None = None
    emoji_name: Annotated[str | None, Field(max_length=32, min_length=1)] = None


class SoundboardSoundResponse(BaseModel):
    name: str
    sound_id: SnowflakeType
    volume: float
    emoji_id: SnowflakeType | None = None
    emoji_name: str | None = None
    guild_id: SnowflakeType | None = None
    available: bool
    user: UserResponse | None = None


class SoundboardSoundSendRequest(BaseModel):
    sound_id: SnowflakeType
    source_guild_id: SnowflakeType | None = None


class SpamLinkRuleResponse(BaseModel):
    id: SnowflakeType
    guild_id: SnowflakeType
    creator_id: SnowflakeType
    name: str
    event_type: AutomodEventType
    actions: list[
        BlockMessageActionResponse
        | FlagToChannelActionResponse
        | QuarantineUserActionResponse
        | UserCommunicationDisabledActionResponse
    ]
    trigger_type: AutomodTriggerType
    enabled: bool | None = None
    exempt_roles: list[SnowflakeType] | None = None
    exempt_channels: list[SnowflakeType] | None = None
    trigger_metadata: SpamLinkTriggerMetadataResponse


class SpamLinkTriggerMetadataResponse(BaseModel):
    pass


class StageInstanceResponse(BaseModel):
    guild_id: SnowflakeType
    channel_id: SnowflakeType
    topic: str
    privacy_level: StageInstancesPrivacyLevels
    id: SnowflakeType
    discoverable_disabled: bool | None = None
    guild_scheduled_event_id: SnowflakeType | None = None


class StageInstancesPrivacyLevels(RootModel[int]):
    root: int


class StageScheduledEventCreateRequest(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    description: Annotated[str | None, Field(max_length=1000)] = None
    image: str | None = None
    scheduled_start_time: datetime
    scheduled_end_time: datetime | None = None
    privacy_level: GuildScheduledEventPrivacyLevels
    entity_type: GuildScheduledEventEntityTypes
    channel_id: SnowflakeType | None = None
    entity_metadata: EntityMetadataStageInstance | None = None


class StageScheduledEventPatchRequestPartial(BaseModel):
    status: GuildScheduledEventStatuses | None = None
    name: Annotated[str | None, Field(max_length=100)] = None
    description: Annotated[str | None, Field(max_length=1000)] = None
    image: str | None = None
    scheduled_start_time: datetime | None = None
    scheduled_end_time: datetime | None = None
    entity_type: GuildScheduledEventEntityTypes | None = None
    privacy_level: GuildScheduledEventPrivacyLevels | None = None
    channel_id: SnowflakeType | None = None
    entity_metadata: EntityMetadataStageInstance | None = None


class StageScheduledEventResponse(BaseModel):
    id: SnowflakeType
    guild_id: SnowflakeType
    name: str
    description: str | None = None
    channel_id: SnowflakeType | None = None
    creator_id: SnowflakeType | None = None
    creator: UserResponse | None = None
    image: str | None = None
    scheduled_start_time: datetime
    scheduled_end_time: datetime | None = None
    status: GuildScheduledEventStatuses
    entity_type: GuildScheduledEventEntityTypes
    entity_id: SnowflakeType | None = None
    user_count: int | None = None
    privacy_level: GuildScheduledEventPrivacyLevels
    user_rsvp: ScheduledEventUserResponse | None = None
    entity_metadata: EntityMetadataStageInstanceResponse | None = None


class StandardStickerResponse(BaseModel):
    id: SnowflakeType
    name: str
    tags: str
    type: StickerTypes
    format_type: StickerFormatTypes | None = None
    description: str | None = None
    pack_id: SnowflakeType
    sort_value: int


class StickerFormatTypes(RootModel[int]):
    root: int


class StickerPackCollectionResponse(BaseModel):
    sticker_packs: list[StickerPackResponse]


class StickerPackResponse(BaseModel):
    id: SnowflakeType
    sku_id: SnowflakeType
    name: str
    description: str | None = None
    stickers: list[StandardStickerResponse]
    cover_sticker_id: SnowflakeType | None = None
    banner_asset_id: SnowflakeType | None = None


class StickerTypes(RootModel[int]):
    root: int


class StringSelectComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    custom_id: Annotated[str, Field(max_length=100)]
    placeholder: Annotated[str | None, Field(max_length=150)] = None
    min_values: Annotated[int | None, Field(ge=0, le=25)] = None
    max_values: Annotated[int | None, Field(ge=1, le=25)] = None
    disabled: bool | None = None
    options: Annotated[
        list[StringSelectOptionForMessageRequest], Field(max_length=25, min_length=1)
    ]


class StringSelectComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    custom_id: str
    placeholder: str | None = None
    min_values: int | None = None
    max_values: int | None = None
    disabled: bool | None = None
    options: list[StringSelectOptionResponse]


class StringSelectOptionForMessageRequest(BaseModel):
    label: Annotated[str, Field(max_length=100, min_length=1)]
    value: Annotated[str, Field(max_length=100, min_length=1)]
    description: Annotated[str | None, Field(max_length=100)] = None
    default: bool | None = None
    emoji: ComponentEmojiForMessageRequest | None = None


class StringSelectOptionResponse(BaseModel):
    label: str
    value: str
    description: str | None = None
    emoji: ComponentEmojiResponse | None = None
    default: bool | None = None


class Tag(RootModel[str]):
    root: Annotated[str, Field(max_length=20)]


class TeamMemberResponse(BaseModel):
    user: UserResponse
    team_id: SnowflakeType
    membership_state: TeamMembershipStates


class TeamMembershipStates(RootModel[int]):
    root: int


class TeamResponse(BaseModel):
    id: SnowflakeType
    icon: str | None = None
    name: str
    owner_user_id: SnowflakeType
    members: list[TeamMemberResponse]


class TextDisplayComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    content: Annotated[str, Field(max_length=4000, min_length=1)]


class TextDisplayComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    content: str


class TextInputComponentForModalRequest(BaseModel):
    type: MessageComponentTypes
    custom_id: Annotated[str, Field(max_length=100)]
    style: TextInputStyleTypes
    label: Annotated[str, Field(max_length=45)]
    value: Annotated[str | None, Field(max_length=4000)] = None
    placeholder: Annotated[str | None, Field(max_length=100)] = None
    required: bool | None = None
    min_length: Annotated[int | None, Field(ge=0, le=4000)] = None
    max_length: Annotated[int | None, Field(ge=1, le=4000)] = None


class TextInputComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    custom_id: str
    style: TextInputStyleTypes
    label: str | None = None
    value: str | None = None
    placeholder: str | None = None
    required: bool | None = None
    min_length: int | None = None
    max_length: int | None = None


class TextInputStyleTypes(RootModel[int]):
    root: int


class ThreadAutoArchiveDuration(RootModel[int]):
    root: int


class ThreadMemberResponse(BaseModel):
    id: SnowflakeType
    user_id: SnowflakeType
    join_timestamp: datetime
    flags: int
    member: GuildMemberResponse | None = None


class ThreadMetadataResponse(BaseModel):
    archived: bool
    archive_timestamp: datetime | None = None
    auto_archive_duration: ThreadAutoArchiveDuration
    locked: bool
    create_timestamp: datetime | None = None
    invitable: bool | None = None


class ThreadResponse(BaseModel):
    id: SnowflakeType
    type: ChannelTypes
    last_message_id: SnowflakeType | None = None
    flags: int
    last_pin_timestamp: datetime | None = None
    guild_id: SnowflakeType
    name: str
    parent_id: SnowflakeType | None = None
    rate_limit_per_user: int | None = None
    bitrate: int | None = None
    user_limit: int | None = None
    rtc_region: str | None = None
    video_quality_mode: VideoQualityModes | None = None
    permissions: str | None = None
    owner_id: SnowflakeType
    thread_metadata: ThreadMetadataResponse | None = None
    message_count: int
    member_count: int
    total_message_sent: int
    applied_tags: list[SnowflakeType] | None = None
    member: ThreadMemberResponse | None = None


class ThreadSearchResponse(BaseModel):
    threads: list[ThreadResponse]
    members: list[ThreadMemberResponse]
    has_more: bool | None = None
    first_messages: list[MessageResponse] | None = None
    total_results: int | None = None


class ThreadSearchTagSetting(RootModel[str]):
    root: str


class ThreadSortOrder(RootModel[int]):
    root: int


class ThreadSortingMode(RootModel[str]):
    root: str


class ThreadsResponse(BaseModel):
    threads: list[ThreadResponse]
    members: list[ThreadMemberResponse]
    has_more: bool | None = None
    first_messages: list[MessageResponse] | None = None


class ThumbnailComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    description: Annotated[str | None, Field(max_length=1024, min_length=1)] = None
    spoiler: bool | None = None
    media: UnfurledMediaRequest


class ThumbnailComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    media: UnfurledMediaResponse
    description: str | None = None
    spoiler: bool


class TypingIndicatorResponse(BaseModel):
    pass


class UInt32Type(RootModel[int]):
    root: Annotated[int, Field(ge=0, le=4294967295)]


class UnfurledMediaRequest(BaseModel):
    url: AnyUrl


class UnfurledMediaRequestWithAttachmentReferenceRequired(BaseModel):
    url: AnyUrl


class UnfurledMediaResponse(BaseModel):
    id: SnowflakeType
    url: str
    proxy_url: str
    width: int | None = None
    height: int | None = None
    content_type: str | None = None


class UpdateDMRequestPartial(BaseModel):
    name: Annotated[str | None, Field(max_length=100, min_length=0)] = None


class UpdateDefaultReactionEmojiRequest(BaseModel):
    emoji_id: SnowflakeType | None = None
    emoji_name: Annotated[str | None, Field(max_length=100)] = None


class UpdateGroupDMRequestPartial(BaseModel):
    name: Annotated[str | None, Field(max_length=100, min_length=0)] = None
    icon: str | None = None


class UpdateGuildChannelRequestPartial(BaseModel):
    type: ChannelTypes | None = None
    name: Annotated[str | None, Field(max_length=100, min_length=1)] = None
    position: Annotated[int | None, Field(ge=0)] = None
    topic: Annotated[str | None, Field(max_length=4096, min_length=0)] = None
    bitrate: Annotated[int | None, Field(ge=8000)] = None
    user_limit: Annotated[int | None, Field(ge=0)] = None
    nsfw: bool | None = None
    rate_limit_per_user: Annotated[int | None, Field(ge=0, le=21600)] = None
    parent_id: SnowflakeType | None = None
    permission_overwrites: Annotated[
        list[ChannelPermissionOverwriteRequest] | None, Field(max_length=100)
    ] = None
    rtc_region: str | None = None
    video_quality_mode: VideoQualityModes | None = None
    default_auto_archive_duration: ThreadAutoArchiveDuration | None = None
    default_reaction_emoji: UpdateDefaultReactionEmojiRequest | None = None
    default_thread_rate_limit_per_user: Annotated[int | None, Field(ge=0, le=21600)] = (
        None
    )
    default_sort_order: ThreadSortOrder | None = None
    default_forum_layout: ForumLayout | None = None
    default_tag_setting: ThreadSearchTagSetting | None = None
    flags: int | None = None
    available_tags: Annotated[
        list[UpdateThreadTagRequest] | None, Field(max_length=20)
    ] = None


class UpdateGuildOnboardingRequest(BaseModel):
    prompts: Annotated[
        list[UpdateOnboardingPromptRequest] | None, Field(max_length=15)
    ] = None
    enabled: bool | None = None
    default_channel_ids: Annotated[
        list[SnowflakeType] | None, Field(max_length=500)
    ] = None
    mode: GuildOnboardingMode | None = None


class UpdateMessageInteractionCallbackRequest(BaseModel):
    type: InteractionCallbackTypes
    data: IncomingWebhookUpdateForInteractionCallbackRequestPartial | None = None


class UpdateMessageInteractionCallbackResponse(BaseModel):
    type: InteractionCallbackTypes
    message: MessageResponse


class UpdateOnboardingPromptRequest(BaseModel):
    title: Annotated[str, Field(max_length=100, min_length=1)]
    options: Annotated[
        list[OnboardingPromptOptionRequest], Field(max_length=50, min_length=1)
    ]
    single_select: bool | None = None
    required: bool | None = None
    in_onboarding: bool | None = None
    type: OnboardingPromptType | None = None
    id: SnowflakeType


class UpdateThreadRequestPartial(BaseModel):
    name: Annotated[str | None, Field(max_length=100, min_length=0)] = None
    archived: bool | None = None
    locked: bool | None = None
    invitable: bool | None = None
    auto_archive_duration: ThreadAutoArchiveDuration | None = None
    rate_limit_per_user: Annotated[int | None, Field(ge=0, le=21600)] = None
    flags: int | None = None
    applied_tags: Annotated[list[SnowflakeType] | None, Field(max_length=5)] = None
    bitrate: Annotated[int | None, Field(ge=8000)] = None
    user_limit: Annotated[int | None, Field(ge=0, le=99)] = None
    rtc_region: str | None = None
    video_quality_mode: VideoQualityModes | None = None


class UpdateThreadTagRequest(BaseModel):
    name: Annotated[str, Field(max_length=20, min_length=0)]
    emoji_id: SnowflakeType | None = None
    emoji_name: Annotated[str | None, Field(max_length=100)] = None
    moderated: bool | None = None
    id: SnowflakeType | None = None


class UserAvatarDecorationResponse(BaseModel):
    asset: str
    sku_id: SnowflakeType | None = None


class UserCollectiblesResponse(BaseModel):
    nameplate: UserNameplateResponse | None = None


class UserCommunicationDisabledAction(BaseModel):
    type: AutomodActionType
    metadata: UserCommunicationDisabledActionMetadata


class UserCommunicationDisabledActionMetadata(BaseModel):
    duration_seconds: Annotated[int | None, Field(ge=0, le=2419200)] = None


class UserCommunicationDisabledActionMetadataResponse(BaseModel):
    duration_seconds: int


class UserCommunicationDisabledActionResponse(BaseModel):
    type: AutomodActionType
    metadata: UserCommunicationDisabledActionMetadataResponse


class UserGuildOnboardingResponse(BaseModel):
    guild_id: SnowflakeType
    prompts: list[OnboardingPromptResponse]
    default_channel_ids: list[SnowflakeType]
    enabled: bool


class UserNameplateResponse(BaseModel):
    sku_id: SnowflakeType | None = None
    asset: str | None = None
    label: str | None = None
    palette: NameplatePalette | None = None


class UserNotificationSettings(RootModel[int]):
    root: int


class UserPIIResponse(BaseModel):
    id: SnowflakeType
    username: str
    avatar: str | None = None
    discriminator: str
    public_flags: int
    flags: UserFlags
    bot: bool | None = None
    system: bool | None = None
    banner: str | None = None
    accent_color: int | None = None
    global_name: str | None = None
    avatar_decoration_data: UserAvatarDecorationResponse | None = None
    collectibles: UserCollectiblesResponse | None = None
    clan: UserPrimaryGuildResponse | None = None
    mfa_enabled: bool
    locale: AvailableLocalesEnum
    premium_type: PremiumTypes | None = None
    email: str | None = None
    verified: bool | None = None


class UserPrimaryGuildResponse(BaseModel):
    pass


class UserResponse(BaseModel):
    id: SnowflakeType
    username: str
    avatar: str | None = None
    discriminator: str
    public_flags: int
    flags: UserFlags
    bot: bool | None = None
    system: bool | None = None
    banner: str | None = None
    accent_color: int | None = None
    global_name: str | None = None
    avatar_decoration_data: UserAvatarDecorationResponse | None = None
    collectibles: UserCollectiblesResponse | None = None
    clan: UserPrimaryGuildResponse | None = None


class UserSelectComponentForMessageRequest(BaseModel):
    type: MessageComponentTypes
    custom_id: Annotated[str, Field(max_length=100)]
    placeholder: Annotated[str | None, Field(max_length=150)] = None
    min_values: Annotated[int | None, Field(ge=0, le=25)] = None
    max_values: Annotated[int | None, Field(ge=1, le=25)] = None
    disabled: bool | None = None
    default_values: Annotated[
        list[UserSelectDefaultValue] | None, Field(max_length=25)
    ] = None


class UserSelectComponentResponse(BaseModel):
    type: MessageComponentTypes
    id: int
    custom_id: str
    placeholder: str | None = None
    min_values: int | None = None
    max_values: int | None = None
    disabled: bool | None = None
    default_values: list[UserSelectDefaultValueResponse] | None = None


class UserSelectDefaultValue(BaseModel):
    type: SnowflakeSelectDefaultValueTypes
    id: SnowflakeType


class UserSelectDefaultValueResponse(BaseModel):
    type: SnowflakeSelectDefaultValueTypes
    id: SnowflakeType


class VanityURLErrorResponse(BaseModel):
    message: str
    code: int


class VanityURLResponse(BaseModel):
    code: str | None = None
    uses: int
    error: VanityURLErrorResponse | None = None


class VerificationLevels(RootModel[int]):
    root: int


class VideoQualityModes(RootModel[int]):
    root: int


class VoiceRegionResponse(BaseModel):
    id: str
    name: str
    custom: bool
    deprecated: bool
    optimal: bool


class VoiceScheduledEventCreateRequest(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    description: Annotated[str | None, Field(max_length=1000)] = None
    image: str | None = None
    scheduled_start_time: datetime
    scheduled_end_time: datetime | None = None
    privacy_level: GuildScheduledEventPrivacyLevels
    entity_type: GuildScheduledEventEntityTypes
    channel_id: SnowflakeType | None = None
    entity_metadata: EntityMetadataVoice | None = None


class VoiceScheduledEventPatchRequestPartial(BaseModel):
    status: GuildScheduledEventStatuses | None = None
    name: Annotated[str | None, Field(max_length=100)] = None
    description: Annotated[str | None, Field(max_length=1000)] = None
    image: str | None = None
    scheduled_start_time: datetime | None = None
    scheduled_end_time: datetime | None = None
    entity_type: GuildScheduledEventEntityTypes | None = None
    privacy_level: GuildScheduledEventPrivacyLevels | None = None
    channel_id: SnowflakeType | None = None
    entity_metadata: EntityMetadataVoice | None = None


class VoiceScheduledEventResponse(BaseModel):
    id: SnowflakeType
    guild_id: SnowflakeType
    name: str
    description: str | None = None
    channel_id: SnowflakeType | None = None
    creator_id: SnowflakeType | None = None
    creator: UserResponse | None = None
    image: str | None = None
    scheduled_start_time: datetime
    scheduled_end_time: datetime | None = None
    status: GuildScheduledEventStatuses
    entity_type: GuildScheduledEventEntityTypes
    entity_id: SnowflakeType | None = None
    user_count: int | None = None
    privacy_level: GuildScheduledEventPrivacyLevels
    user_rsvp: ScheduledEventUserResponse | None = None
    entity_metadata: EntityMetadataVoiceResponse | None = None


class VoiceStateResponse(BaseModel):
    channel_id: SnowflakeType | None = None
    deaf: bool
    guild_id: SnowflakeType | None = None
    member: GuildMemberResponse | None = None
    mute: bool
    request_to_speak_timestamp: datetime | None = None
    suppress: bool
    self_stream: bool | None = None
    self_deaf: bool
    self_mute: bool
    self_video: bool
    session_id: str
    user_id: SnowflakeType


class WebhookSlackEmbed(BaseModel):
    title: Annotated[str | None, Field(max_length=152133)] = None
    title_link: AnyUrl | None = None
    text: Annotated[str | None, Field(max_length=152133)] = None
    color: Annotated[
        str | None,
        Field(max_length=7, pattern="^#(([0-9a-fA-F]{2}){3}|([0-9a-fA-F]){3})$"),
    ] = None
    ts: int | None = None
    pretext: Annotated[str | None, Field(max_length=152133)] = None
    footer: Annotated[str | None, Field(max_length=152133)] = None
    footer_icon: AnyUrl | None = None
    author_name: Annotated[str | None, Field(max_length=152133)] = None
    author_link: AnyUrl | None = None
    author_icon: AnyUrl | None = None
    image_url: AnyUrl | None = None
    thumb_url: AnyUrl | None = None
    fields: Annotated[list[WebhookSlackEmbedField] | None, Field(max_length=1521)] = (
        None
    )


class WebhookSlackEmbedField(BaseModel):
    name: Annotated[str | None, Field(max_length=152133)] = None
    value: Annotated[str | None, Field(max_length=152133)] = None
    inline: bool | None = None


class WebhookSourceChannelResponse(BaseModel):
    id: SnowflakeType
    name: str


class WebhookSourceGuildResponse(BaseModel):
    id: SnowflakeType
    icon: str | None = None
    name: str


class WebhookTypes(RootModel[int]):
    root: int


class WelcomeMessageResponse(BaseModel):
    author_ids: list[SnowflakeType]
    message: str


class WelcomeScreenPatchRequestPartial(BaseModel):
    description: Annotated[str | None, Field(max_length=140)] = None
    welcome_channels: Annotated[
        list[GuildWelcomeChannel] | None, Field(max_length=5)
    ] = None
    enabled: bool | None = None


class WidgetActivity(BaseModel):
    name: str


class WidgetChannel(BaseModel):
    id: SnowflakeType
    name: str
    position: int


class WidgetImageStyles(RootModel[str]):
    root: str


class WidgetMember(BaseModel):
    id: str
    username: str
    discriminator: WidgetUserDiscriminator
    avatar: None = None
    status: str
    avatar_url: AnyUrl
    activity: WidgetActivity | None = None
    deaf: bool | None = None
    mute: bool | None = None
    self_deaf: bool | None = None
    self_mute: bool | None = None
    suppress: bool | None = None
    channel_id: SnowflakeType | None = None


class WidgetResponse(BaseModel):
    id: SnowflakeType
    name: str
    instant_invite: str | None = None
    channels: list[WidgetChannel]
    members: list[WidgetMember]
    presence_count: int


class WidgetSettingsResponse(BaseModel):
    enabled: bool
    channel_id: SnowflakeType | None = None


class WidgetUserDiscriminator(RootModel[str]):
    root: str


ErrorDetails.model_rebuild()
