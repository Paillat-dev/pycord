from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, RootModel

from ..schemas import (
    ApplicationCommandPermission,
    ApplicationCommandResponse,
    ApplicationCommandUpdateRequest,
    ApplicationRoleConnectionsMetadataItemRequest,
    ApplicationRoleConnectionsMetadataItemResponse,
    CommandPermissionsResponse,
    EntitlementResponse,
    SnowflakeType,
)


class ApplicationsApplicationIdAttachmentPostRequest(BaseModel):
    file: str


class ApplicationsApplicationIdCommandsGetResponse(
    RootModel[list[ApplicationCommandResponse]]
):
    root: list[ApplicationCommandResponse]


class ApplicationsApplicationIdCommandsPutRequest(
    RootModel[list[ApplicationCommandUpdateRequest]]
):
    root: Annotated[list[ApplicationCommandUpdateRequest], Field(max_length=110)]


class ApplicationsApplicationIdCommandsPutResponse(
    RootModel[list[ApplicationCommandResponse]]
):
    root: list[ApplicationCommandResponse]


class ApplicationsApplicationIdEmojisEmojiIdPatchRequest(BaseModel):
    name: Annotated[str | None, Field(max_length=32, min_length=2)] = None


class ApplicationsApplicationIdEmojisPostRequest(BaseModel):
    name: Annotated[str, Field(max_length=32, min_length=2)]
    image: str


class ApplicationsApplicationIdEntitlementsGetResponse(
    RootModel[list[EntitlementResponse | None]]
):
    root: list[EntitlementResponse | None]


class ApplicationsApplicationIdGuildsGuildIdCommandsCommandIdPermissionsPutRequest(
    BaseModel
):
    permissions: Annotated[
        list[ApplicationCommandPermission] | None, Field(max_length=100)
    ] = None


class ApplicationsApplicationIdGuildsGuildIdCommandsGetResponse(
    RootModel[list[ApplicationCommandResponse]]
):
    root: list[ApplicationCommandResponse]


class ApplicationsApplicationIdGuildsGuildIdCommandsPermissionsGetResponse(
    RootModel[list[CommandPermissionsResponse]]
):
    root: list[CommandPermissionsResponse]


class ApplicationsApplicationIdGuildsGuildIdCommandsPutRequest(
    RootModel[list[ApplicationCommandUpdateRequest]]
):
    root: Annotated[list[ApplicationCommandUpdateRequest], Field(max_length=110)]


class ApplicationsApplicationIdGuildsGuildIdCommandsPutResponse(
    RootModel[list[ApplicationCommandResponse]]
):
    root: list[ApplicationCommandResponse]


class ApplicationsApplicationIdRoleConnectionsMetadataGetResponse(
    RootModel[list[ApplicationRoleConnectionsMetadataItemResponse]]
):
    root: list[ApplicationRoleConnectionsMetadataItemResponse]


class ApplicationsApplicationIdRoleConnectionsMetadataPutRequest(
    RootModel[list[ApplicationRoleConnectionsMetadataItemRequest]]
):
    root: Annotated[
        list[ApplicationRoleConnectionsMetadataItemRequest], Field(max_length=5)
    ]


class ApplicationsApplicationIdRoleConnectionsMetadataPutResponse(
    RootModel[list[ApplicationRoleConnectionsMetadataItemResponse]]
):
    root: list[ApplicationRoleConnectionsMetadataItemResponse]


class SkuIds(RootModel[list[SnowflakeType | None]]):
    root: Annotated[list[SnowflakeType | None], Field(max_length=100)]
