from __future__ import annotations

from pydantic import AnyUrl, BaseModel, Field, RootModel

from ..schemas import FriendInviteResponse, GroupDMInviteResponse, GuildInviteResponse


class InvitesCodeDeleteResponse(
    RootModel[FriendInviteResponse | GroupDMInviteResponse | GuildInviteResponse]
):
    root: FriendInviteResponse | GroupDMInviteResponse | GuildInviteResponse


class InvitesCodeGetResponse(
    RootModel[FriendInviteResponse | GroupDMInviteResponse | GuildInviteResponse]
):
    root: FriendInviteResponse | GroupDMInviteResponse | GuildInviteResponse
