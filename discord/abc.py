"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Pycord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import asyncio
import copy
import time
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    Protocol,
    Sequence,
    TypeVar,
    Union,
    overload,
    runtime_checkable,
)

from . import utils
from .context_managers import Typing
from .enums import ChannelType
from .errors import ClientException, InvalidArgument
from .file import File, VoiceMessage
from .flags import ChannelFlags, MessageFlags
from .invite import Invite
from .iterators import HistoryIterator
from .mentions import AllowedMentions
from .partial_emoji import PartialEmoji, _EmojiTag
from .permissions import PermissionOverwrite, Permissions
from .role import Role
from .scheduled_events import ScheduledEvent
from .sticker import GuildSticker, StickerItem
from .voice_client import VoiceClient, VoiceProtocol

__all__ = (
    "Snowflake",
    "User",
    "PrivateChannel",
    "GuildChannel",
    "Messageable",
    "Connectable",
    "Mentionable",
)

T = TypeVar("T", bound=VoiceProtocol)

if TYPE_CHECKING:
    from datetime import datetime

    from .asset import Asset
    from .channel import (
        CategoryChannel,
        DMChannel,
        GroupChannel,
        PartialMessageable,
        StageChannel,
        TextChannel,
        VoiceChannel,
    )
    from .client import Client
    from .embeds import Embed
    from .enums import InviteTarget
    from .guild import Guild
    from .member import Member
    from .message import Message, MessageReference, PartialMessage
    from .poll import Poll
    from .state import ConnectionState
    from .threads import Thread
    from .types.channel import Channel as ChannelPayload
    from .types.channel import GuildChannel as GuildChannelPayload
    from .types.channel import OverwriteType
    from .types.channel import PermissionOverwrite as PermissionOverwritePayload
    from .ui.view import View
    from .user import ClientUser

    PartialMessageableChannel = Union[
        TextChannel, VoiceChannel, StageChannel, Thread, DMChannel, PartialMessageable
    ]
    MessageableChannel = Union[PartialMessageableChannel, GroupChannel]
    SnowflakeTime = Union["Snowflake", datetime]

MISSING = utils.MISSING


async def _single_delete_strategy(
    messages: Iterable[Message], *, reason: str | None = None
):
    for m in messages:
        await m.delete(reason=reason)


async def _purge_messages_helper(
    channel: TextChannel | StageChannel | Thread | VoiceChannel,
    *,
    limit: int | None = 100,
    check: Callable[[Message], bool] = MISSING,
    before: SnowflakeTime | None = None,
    after: SnowflakeTime | None = None,
    around: SnowflakeTime | None = None,
    oldest_first: bool | None = False,
    bulk: bool = True,
    reason: str | None = None,
) -> list[Message]:
    if check is MISSING:
        check = lambda m: True

    iterator = channel.history(
        limit=limit,
        before=before,
        after=after,
        oldest_first=oldest_first,
        around=around,
    )
    ret: list[Message] = []
    count = 0

    minimum_time = int((time.time() - 14 * 24 * 60 * 60) * 1000.0 - 1420070400000) << 22
    strategy = channel.delete_messages if bulk else _single_delete_strategy

    async for message in iterator:
        if count == 100:
            to_delete = ret[-100:]
            await strategy(to_delete, reason=reason)
            count = 0
            await asyncio.sleep(1)

        if not check(message):
            continue

        if message.id < minimum_time:
            # older than 14 days old
            if count == 1:
                await ret[-1].delete(reason=reason)
            elif count >= 2:
                to_delete = ret[-count:]
                await strategy(to_delete, reason=reason)

            count = 0
            strategy = _single_delete_strategy

        count += 1
        ret.append(message)

    # Some messages remaining to poll
    if count >= 2:
        # more than 2 messages -> bulk delete
        to_delete = ret[-count:]
        await strategy(to_delete, reason=reason)
    elif count == 1:
        # delete a single message
        await ret[-1].delete(reason=reason)

    return ret


@runtime_checkable
class Snowflake(Protocol):
    """An ABC that details the common operations on a Discord model.

    Almost all :ref:`Discord models <discord_api_models>` meet this
    abstract base class.

    If you want to create a snowflake on your own, consider using
    :class:`.Object`.

    Attributes
    ----------
    id: :class:`int`
        The model's unique ID.
    """

    __slots__ = ()
    id: int


@runtime_checkable
class User(Snowflake, Protocol):
    """An ABC that details the common operations on a Discord user.

    The following implement this ABC:

    - :class:`~discord.User`
    - :class:`~discord.ClientUser`
    - :class:`~discord.Member`

    This ABC must also implement :class:`~discord.abc.Snowflake`.

    Attributes
    ----------
    name: :class:`str`
        The user's username.
    discriminator: :class:`str`
        The user's discriminator.

        .. note::

            If the user has migrated to the new username system, this will always be "0".
    global_name: :class:`str`
        The user's global name.

        .. versionadded:: 2.5
    avatar: :class:`~discord.Asset`
        The avatar asset the user has.
    bot: :class:`bool`
        If the user is a bot account.
    """

    __slots__ = ()

    name: str
    discriminator: str
    global_name: str | None
    avatar: Asset
    bot: bool

    @property
    def display_name(self) -> str:
        """Returns the user's display name."""
        raise NotImplementedError

    @property
    def mention(self) -> str:
        """Returns a string that allows you to mention the given user."""
        raise NotImplementedError


@runtime_checkable
class PrivateChannel(Snowflake, Protocol):
    """An ABC that details the common operations on a private Discord channel.

    The following implement this ABC:

    - :class:`~discord.DMChannel`
    - :class:`~discord.GroupChannel`

    This ABC must also implement :class:`~discord.abc.Snowflake`.

    Attributes
    ----------
    me: :class:`~discord.ClientUser`
        The user presenting yourself.
    """

    __slots__ = ()

    me: ClientUser


class _Overwrites:
    __slots__ = ("id", "allow", "deny", "type")

    ROLE = 0
    MEMBER = 1

    def __init__(self, data: PermissionOverwritePayload):
        self.id: int = int(data["id"])
        self.allow: int = int(data.get("allow", 0))
        self.deny: int = int(data.get("deny", 0))
        self.type: OverwriteType = data["type"]

    def _asdict(self) -> PermissionOverwritePayload:
        return {
            "id": self.id,
            "allow": str(self.allow),
            "deny": str(self.deny),
            "type": self.type,
        }

    def is_role(self) -> bool:
        return self.type == self.ROLE

    def is_member(self) -> bool:
        return self.type == self.MEMBER


GCH = TypeVar("GCH", bound="GuildChannel")


class GuildChannel:
    """An ABC that details the common operations on a Discord guild channel.

    The following implement this ABC:

    - :class:`~discord.TextChannel`
    - :class:`~discord.VoiceChannel`
    - :class:`~discord.CategoryChannel`
    - :class:`~discord.StageChannel`
    - :class:`~discord.ForumChannel`

    This ABC must also implement :class:`~discord.abc.Snowflake`.

    Attributes
    ----------
    name: :class:`str`
        The channel name.
    guild: :class:`~discord.Guild`
        The guild the channel belongs to.
    position: :class:`int`
        The position in the channel list. This is a number that starts at 0.
        e.g. the top channel is position 0.
    """

    __slots__ = ()

    id: int
    name: str
    guild: Guild
    type: ChannelType
    position: int
    category_id: int | None
    flags: ChannelFlags
    _state: ConnectionState
    _overwrites: list[_Overwrites]

    if TYPE_CHECKING:

        def __init__(
            self, *, state: ConnectionState, guild: Guild, data: dict[str, Any]
        ): ...

    def __str__(self) -> str:
        return self.name

    @property
    def _sorting_bucket(self) -> int:
        raise NotImplementedError

    def _update(self, guild: Guild, data: dict[str, Any]) -> None:
        raise NotImplementedError

    async def _move(
        self,
        position: int,
        parent_id: Any | None = None,
        lock_permissions: bool = False,
        *,
        reason: str | None,
    ) -> None:
        if position < 0:
            raise InvalidArgument("Channel position cannot be less than 0.")

        http = self._state.http
        bucket = self._sorting_bucket
        channels: list[GuildChannel] = [
            c for c in self.guild.channels if c._sorting_bucket == bucket
        ]

        channels.sort(key=lambda c: c.position)

        try:
            # remove ourselves from the channel list
            channels.remove(self)
        except ValueError:
            # not there somehow lol
            return
        else:
            index = next(
                (i for i, c in enumerate(channels) if c.position >= position),
                len(channels),
            )
            # add ourselves at our designated position
            channels.insert(index, self)

        payload = []
        for index, c in enumerate(channels):
            d: dict[str, Any] = {"id": c.id, "position": index}
            if parent_id is not MISSING and c.id == self.id:
                d.update(parent_id=parent_id, lock_permissions=lock_permissions)
            payload.append(d)

        await http.bulk_channel_update(self.guild.id, payload, reason=reason)

    async def _edit(
        self, options: dict[str, Any], reason: str | None
    ) -> ChannelPayload | None:
        try:
            parent = options.pop("category")
        except KeyError:
            parent_id = MISSING
        else:
            parent_id = parent and parent.id

        try:
            options["rate_limit_per_user"] = options.pop("slowmode_delay")
        except KeyError:
            pass

        try:
            options["default_thread_rate_limit_per_user"] = options.pop(
                "default_thread_slowmode_delay"
            )
        except KeyError:
            pass

        try:
            options["flags"] = options.pop("flags").value
        except KeyError:
            pass

        try:
            options["available_tags"] = [
                tag.to_dict() for tag in options.pop("available_tags")
            ]
        except KeyError:
            pass

        try:
            rtc_region = options.pop("rtc_region")
        except KeyError:
            pass
        else:
            options["rtc_region"] = None if rtc_region is None else str(rtc_region)

        try:
            video_quality_mode = options.pop("video_quality_mode")
        except KeyError:
            pass
        else:
            options["video_quality_mode"] = int(video_quality_mode)

        lock_permissions = options.pop("sync_permissions", False)

        try:
            position = options.pop("position")
        except KeyError:
            if parent_id is not MISSING:
                if lock_permissions:
                    category = self.guild.get_channel(parent_id)
                    if category:
                        options["permission_overwrites"] = [
                            c._asdict() for c in category._overwrites
                        ]
                options["parent_id"] = parent_id
            elif lock_permissions and self.category_id is not None:
                # if we're syncing permissions on a pre-existing channel category without changing it
                # we need to update the permissions to point to the pre-existing category
                category = self.guild.get_channel(self.category_id)
                if category:
                    options["permission_overwrites"] = [
                        c._asdict() for c in category._overwrites
                    ]
        else:
            await self._move(
                position,
                parent_id=parent_id,
                lock_permissions=lock_permissions,
                reason=reason,
            )

        overwrites = options.get("overwrites")
        if overwrites is not None:
            perms = []
            for target, perm in overwrites.items():
                if not isinstance(perm, PermissionOverwrite):
                    raise InvalidArgument(
                        "Expected PermissionOverwrite received"
                        f" {perm.__class__.__name__}"
                    )

                allow, deny = perm.pair()
                payload = {
                    "allow": allow.value,
                    "deny": deny.value,
                    "id": target.id,
                    "type": (
                        _Overwrites.ROLE
                        if isinstance(target, Role)
                        else _Overwrites.MEMBER
                    ),
                }

                perms.append(payload)
            options["permission_overwrites"] = perms

        try:
            ch_type = options["type"]
        except KeyError:
            pass
        else:
            if not isinstance(ch_type, ChannelType):
                raise InvalidArgument("type field must be of type ChannelType")
            options["type"] = ch_type.value

        try:
            default_reaction_emoji = options["default_reaction_emoji"]
        except KeyError:
            pass
        else:
            if isinstance(
                default_reaction_emoji, _EmojiTag
            ):  # GuildEmoji, PartialEmoji
                default_reaction_emoji = default_reaction_emoji._to_partial()
            elif isinstance(default_reaction_emoji, int):
                default_reaction_emoji = PartialEmoji(
                    name=None, id=default_reaction_emoji
                )
            elif isinstance(default_reaction_emoji, str):
                default_reaction_emoji = PartialEmoji.from_str(default_reaction_emoji)
            elif default_reaction_emoji is None:
                pass
            else:
                raise InvalidArgument(
                    "default_reaction_emoji must be of type: GuildEmoji | int | str | None"
                )

            options["default_reaction_emoji"] = (
                default_reaction_emoji._to_forum_reaction_payload()
                if default_reaction_emoji
                else None
            )

        if options:
            return await self._state.http.edit_channel(
                self.id, reason=reason, **options
            )

    def _fill_overwrites(self, data: GuildChannelPayload) -> None:
        self._overwrites = []
        everyone_index = 0
        everyone_id = self.guild.id

        for index, overridden in enumerate(data.get("permission_overwrites", [])):
            overwrite = _Overwrites(overridden)
            self._overwrites.append(overwrite)

            if overwrite.type == _Overwrites.MEMBER:
                continue

            if overwrite.id == everyone_id:
                # the @everyone role is not guaranteed to be the first one
                # in the list of permission overwrites, however the permission
                # resolution code kind of requires that it is the first one in
                # the list since it is special. So we need the index so we can
                # swap it to be the first one.
                everyone_index = index

        # do the swap
        tmp = self._overwrites
        if tmp:
            tmp[everyone_index], tmp[0] = tmp[0], tmp[everyone_index]

    @property
    def changed_roles(self) -> list[Role]:
        """Returns a list of roles that have been overridden from
        their default values in the :attr:`~discord.Guild.roles` attribute.
        """
        ret = []
        g = self.guild
        for overwrite in filter(lambda o: o.is_role(), self._overwrites):
            role = g.get_role(overwrite.id)
            if role is None:
                continue

            role = copy.copy(role)
            role.permissions.handle_overwrite(overwrite.allow, overwrite.deny)
            ret.append(role)
        return ret

    @property
    def mention(self) -> str:
        """The string that allows you to mention the channel."""
        return f"<#{self.id}>"

    @property
    def jump_url(self) -> str:
        """Returns a URL that allows the client to jump to the channel.

        .. versionadded:: 2.0
        """
        return f"https://discord.com/channels/{self.guild.id}/{self.id}"

    @property
    def created_at(self) -> datetime:
        """Returns the channel's creation time in UTC."""
        return utils.snowflake_time(self.id)

    def overwrites_for(self, obj: Role | User) -> PermissionOverwrite:
        """Returns the channel-specific overwrites for a member or a role.

        Parameters
        ----------
        obj: Union[:class:`~discord.Role`, :class:`~discord.abc.User`]
            The role or user denoting
            whose overwrite to get.

        Returns
        -------
        :class:`~discord.PermissionOverwrite`
            The permission overwrites for this object.
        """

        if isinstance(obj, User):
            predicate = lambda p: p.is_member()
        elif isinstance(obj, Role):
            predicate = lambda p: p.is_role()
        else:
            predicate = lambda p: True

        for overwrite in filter(predicate, self._overwrites):
            if overwrite.id == obj.id:
                allow = Permissions(overwrite.allow)
                deny = Permissions(overwrite.deny)
                return PermissionOverwrite.from_pair(allow, deny)

        return PermissionOverwrite()

    @property
    def overwrites(self) -> dict[Role | Member, PermissionOverwrite]:
        """Returns all of the channel's overwrites.

        This is returned as a dictionary where the key contains the target which
        can be either a :class:`~discord.Role` or a :class:`~discord.Member` and the value is the
        overwrite as a :class:`~discord.PermissionOverwrite`.

        Returns
        -------
        Dict[Union[:class:`~discord.Role`, :class:`~discord.Member`], :class:`~discord.PermissionOverwrite`]
            The channel's permission overwrites.
        """
        ret = {}
        for ow in self._overwrites:
            allow = Permissions(ow.allow)
            deny = Permissions(ow.deny)
            overwrite = PermissionOverwrite.from_pair(allow, deny)
            target = None

            if ow.is_role():
                target = self.guild.get_role(ow.id)
            elif ow.is_member():
                target = self.guild.get_member(ow.id)

            # TODO: There is potential data loss here in the non-chunked
            # case, i.e. target is None because get_member returned nothing.
            # This can be fixed with a slight breaking change to the return type,
            # i.e. adding discord.Object to the list of it
            # However, for now this is an acceptable compromise.
            if target is not None:
                ret[target] = overwrite
        return ret

    @property
    def category(self) -> CategoryChannel | None:
        """The category this channel belongs to.

        If there is no category then this is ``None``.
        """
        return self.guild.get_channel(self.category_id)  # type: ignore

    @property
    def permissions_synced(self) -> bool:
        """Whether the permissions for this channel are synced with the
        category it belongs to.

        If there is no category then this is ``False``.

        .. versionadded:: 1.3
        """
        if self.category_id is None:
            return False

        category = self.guild.get_channel(self.category_id)
        return bool(category and category.overwrites == self.overwrites)

    def permissions_for(self, obj: Member | Role, /) -> Permissions:
        """Handles permission resolution for the :class:`~discord.Member`
        or :class:`~discord.Role`.

        This function takes into consideration the following cases:

        - Guild owner
        - Guild roles
        - Channel overrides
        - Member overrides

        If a :class:`~discord.Role` is passed, then it checks the permissions
        someone with that role would have, which is essentially:

        - The default role permissions
        - The permissions of the role used as a parameter
        - The default role permission overwrites
        - The permission overwrites of the role used as a parameter

        .. versionchanged:: 2.0
            The object passed in can now be a role object.

        Parameters
        ----------
        obj: Union[:class:`~discord.Member`, :class:`~discord.Role`]
            The object to resolve permissions for. This could be either
            a member or a role. If it's a role then member overwrites
            are not computed.

        Returns
        -------
        :class:`~discord.Permissions`
            The resolved permissions for the member or role.
        """

        # The current cases can be explained as:
        # Guild owner get all permissions -- no questions asked. Otherwise...
        # The @everyone role gets the first application.
        # After that, the applied roles that the user has in the channel
        # (or otherwise) are then OR'd together.
        # After the role permissions are resolved, the member permissions
        # have to take into effect.
        # After all that is done, you have to do the following:

        # If manage permissions is True, then all permissions are set to True.

        # The operation first takes into consideration the denied
        # and then the allowed.

        if self.guild.owner_id == obj.id:
            return Permissions.all()

        default = self.guild.default_role
        base = Permissions(default.permissions.value if default else 0)

        # Handle the role case first
        if isinstance(obj, Role):
            base.value |= obj._permissions

            if base.administrator:
                return Permissions.all()

            # Apply @everyone allow/deny first since it's special
            try:
                maybe_everyone = self._overwrites[0]
                if maybe_everyone.id == self.guild.id:
                    base.handle_overwrite(
                        allow=maybe_everyone.allow, deny=maybe_everyone.deny
                    )
            except IndexError:
                pass

            if obj.is_default():
                return base

            overwrite = utils.get(self._overwrites, type=_Overwrites.ROLE, id=obj.id)
            if overwrite is not None:
                base.handle_overwrite(overwrite.allow, overwrite.deny)

            return base

        roles = obj._roles
        get_role = self.guild.get_role

        # Apply guild roles that the member has.
        for role_id in roles:
            role = get_role(role_id)
            if role is not None:
                base.value |= role._permissions

        # Guild-wide Administrator -> True for everything
        # Bypass all channel-specific overrides
        if base.administrator:
            return Permissions.all()

        # Apply @everyone allow/deny first since it's special
        try:
            maybe_everyone = self._overwrites[0]
            if maybe_everyone.id == self.guild.id:
                base.handle_overwrite(
                    allow=maybe_everyone.allow, deny=maybe_everyone.deny
                )
                remaining_overwrites = self._overwrites[1:]
            else:
                remaining_overwrites = self._overwrites
        except IndexError:
            remaining_overwrites = self._overwrites

        denies = 0
        allows = 0

        # Apply channel specific role permission overwrites
        for overwrite in remaining_overwrites:
            if overwrite.is_role() and roles.has(overwrite.id):
                denies |= overwrite.deny
                allows |= overwrite.allow

        base.handle_overwrite(allow=allows, deny=denies)

        # Apply member specific permission overwrites
        for overwrite in remaining_overwrites:
            if overwrite.is_member() and overwrite.id == obj.id:
                base.handle_overwrite(allow=overwrite.allow, deny=overwrite.deny)
                break

        # if you can't send a message in a channel then you can't have certain
        # permissions as well
        if not base.send_messages:
            base.send_tts_messages = False
            base.mention_everyone = False
            base.embed_links = False
            base.attach_files = False

        # if you can't read a channel then you have no permissions there
        if not base.read_messages:
            denied = Permissions.all_channel()
            base.value &= ~denied.value

        return base

    async def delete(self, *, reason: str | None = None) -> None:
        """|coro|

        Deletes the channel.

        You must have :attr:`~discord.Permissions.manage_channels` permission to use this.

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason for deleting this channel.
            Shows up on the audit log.

        Raises
        ------
        ~discord.Forbidden
            You do not have proper permissions to delete the channel.
        ~discord.NotFound
            The channel was not found or was already deleted.
        ~discord.HTTPException
            Deleting the channel failed.
        """
        await self._state.http.delete_channel(self.id, reason=reason)

    @overload
    async def set_permissions(
        self,
        target: Member | Role,
        *,
        overwrite: PermissionOverwrite | None = ...,
        reason: str | None = ...,
    ) -> None: ...

    @overload
    async def set_permissions(
        self,
        target: Member | Role,
        *,
        reason: str | None = ...,
        **permissions: bool,
    ) -> None: ...

    async def set_permissions(
        self, target, *, overwrite=MISSING, reason=None, **permissions
    ):
        r"""|coro|

        Sets the channel specific permission overwrites for a target in the
        channel.

        The ``target`` parameter should either be a :class:`~discord.Member` or a
        :class:`~discord.Role` that belongs to guild.

        The ``overwrite`` parameter, if given, must either be ``None`` or
        :class:`~discord.PermissionOverwrite`. For convenience, you can pass in
        keyword arguments denoting :class:`~discord.Permissions` attributes. If this is
        done, then you cannot mix the keyword arguments with the ``overwrite``
        parameter.

        If the ``overwrite`` parameter is ``None``, then the permission
        overwrites are deleted.

        You must have the :attr:`~discord.Permissions.manage_roles` permission to use this.

        .. note::

            This method *replaces* the old overwrites with the ones given.

        Examples
        ----------

        Setting allow and deny: ::

            await message.channel.set_permissions(message.author, read_messages=True,
                                                                  send_messages=False)

        Deleting overwrites ::

            await channel.set_permissions(member, overwrite=None)

        Using :class:`~discord.PermissionOverwrite` ::

            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            overwrite.read_messages = True
            await channel.set_permissions(member, overwrite=overwrite)

        Parameters
        -----------
        target: Union[:class:`~discord.Member`, :class:`~discord.Role`]
            The member or role to overwrite permissions for.
        overwrite: Optional[:class:`~discord.PermissionOverwrite`]
            The permissions to allow and deny to the target, or ``None`` to
            delete the overwrite.
        \*\*permissions
            A keyword argument list of permissions to set for ease of use.
            Cannot be mixed with ``overwrite``.
        reason: Optional[:class:`str`]
            The reason for doing this action. Shows up on the audit log.

        Raises
        -------
        ~discord.Forbidden
            You do not have permissions to edit channel specific permissions.
        ~discord.HTTPException
            Editing channel specific permissions failed.
        ~discord.NotFound
            The role or member being edited is not part of the guild.
        ~discord.InvalidArgument
            The overwrite parameter invalid or the target type was not
            :class:`~discord.Role` or :class:`~discord.Member`.
        """

        http = self._state.http

        if isinstance(target, User):
            perm_type = _Overwrites.MEMBER
        elif isinstance(target, Role):
            perm_type = _Overwrites.ROLE
        else:
            raise InvalidArgument("target parameter must be either Member or Role")

        if overwrite is MISSING:
            if len(permissions) == 0:
                raise InvalidArgument("No overwrite provided.")
            try:
                overwrite = PermissionOverwrite(**permissions)
            except (ValueError, TypeError):
                raise InvalidArgument("Invalid permissions given to keyword arguments.")
        elif len(permissions) > 0:
            raise InvalidArgument("Cannot mix overwrite and keyword arguments.")

        # TODO: wait for event

        if overwrite is None:
            await http.delete_channel_permissions(self.id, target.id, reason=reason)
        elif isinstance(overwrite, PermissionOverwrite):
            (allow, deny) = overwrite.pair()
            await http.edit_channel_permissions(
                self.id, target.id, allow.value, deny.value, perm_type, reason=reason
            )
        else:
            raise InvalidArgument("Invalid overwrite type provided.")

    async def _clone_impl(
        self: GCH,
        base_attrs: dict[str, Any],
        *,
        name: str | None = None,
        reason: str | None = None,
    ) -> GCH:
        base_attrs["permission_overwrites"] = [x._asdict() for x in self._overwrites]
        base_attrs["parent_id"] = self.category_id
        base_attrs["name"] = name or self.name
        guild_id = self.guild.id
        cls = self.__class__
        data = await self._state.http.create_channel(
            guild_id, self.type.value, reason=reason, **base_attrs
        )
        obj = cls(state=self._state, guild=self.guild, data=data)

        # temporarily add it to the cache
        self.guild._channels[obj.id] = obj  # type: ignore
        return obj

    async def clone(
        self: GCH, *, name: str | None = None, reason: str | None = None
    ) -> GCH:
        """|coro|

        Clones this channel. This creates a channel with the same properties
        as this channel.

        You must have the :attr:`~discord.Permissions.manage_channels` permission to
        do this.

        .. versionadded:: 1.1

        Parameters
        ----------
        name: Optional[:class:`str`]
            The name of the new channel. If not provided, defaults to this
            channel name.
        reason: Optional[:class:`str`]
            The reason for cloning this channel. Shows up on the audit log.

        Returns
        -------
        :class:`.abc.GuildChannel`
            The channel that was created.

        Raises
        ------
        ~discord.Forbidden
            You do not have the proper permissions to create this channel.
        ~discord.HTTPException
            Creating the channel failed.
        """
        raise NotImplementedError

    @overload
    async def move(
        self,
        *,
        beginning: bool,
        offset: int = MISSING,
        category: Snowflake | None = MISSING,
        sync_permissions: bool = MISSING,
        reason: str | None = MISSING,
    ) -> None: ...

    @overload
    async def move(
        self,
        *,
        end: bool,
        offset: int = MISSING,
        category: Snowflake | None = MISSING,
        sync_permissions: bool = MISSING,
        reason: str = MISSING,
    ) -> None: ...

    @overload
    async def move(
        self,
        *,
        before: Snowflake,
        offset: int = MISSING,
        category: Snowflake | None = MISSING,
        sync_permissions: bool = MISSING,
        reason: str = MISSING,
    ) -> None: ...

    @overload
    async def move(
        self,
        *,
        after: Snowflake,
        offset: int = MISSING,
        category: Snowflake | None = MISSING,
        sync_permissions: bool = MISSING,
        reason: str = MISSING,
    ) -> None: ...

    async def move(self, **kwargs) -> None:
        """|coro|

        A rich interface to help move a channel relative to other channels.

        If exact position movement is required, ``edit`` should be used instead.

        You must have the :attr:`~discord.Permissions.manage_channels` permission to
        do this.

        .. note::

            Voice channels will always be sorted below text channels.
            This is a Discord limitation.

        .. versionadded:: 1.7

        Parameters
        ----------
        beginning: :class:`bool`
            Whether to move the channel to the beginning of the
            channel list (or category if given).
            This is mutually exclusive with ``end``, ``before``, and ``after``.
        end: :class:`bool`
            Whether to move the channel to the end of the
            channel list (or category if given).
            This is mutually exclusive with ``beginning``, ``before``, and ``after``.
        before: :class:`~discord.abc.Snowflake`
            The channel that should be before our current channel.
            This is mutually exclusive with ``beginning``, ``end``, and ``after``.
        after: :class:`~discord.abc.Snowflake`
            The channel that should be after our current channel.
            This is mutually exclusive with ``beginning``, ``end``, and ``before``.
        offset: :class:`int`
            The number of channels to offset the move by. For example,
            an offset of ``2`` with ``beginning=True`` would move
            it 2 after the beginning. A positive number moves it below
            while a negative number moves it above. Note that this
            number is relative and computed after the ``beginning``,
            ``end``, ``before``, and ``after`` parameters.
        category: Optional[:class:`~discord.abc.Snowflake`]
            The category to move this channel under.
            If ``None`` is given then it moves it out of the category.
            This parameter is ignored if moving a category channel.
        sync_permissions: :class:`bool`
            Whether to sync the permissions with the category (if given).
        reason: :class:`str`
            The reason for the move.

        Raises
        ------
        InvalidArgument
            An invalid position was given or a bad mix of arguments was passed.
        Forbidden
            You do not have permissions to move the channel.
        HTTPException
            Moving the channel failed.
        """

        if not kwargs:
            return

        beginning, end = kwargs.get("beginning"), kwargs.get("end")
        before, after = kwargs.get("before"), kwargs.get("after")
        offset = kwargs.get("offset", 0)
        if sum(bool(a) for a in (beginning, end, before, after)) > 1:
            raise InvalidArgument(
                "Only one of [before, after, end, beginning] can be used."
            )

        bucket = self._sorting_bucket
        parent_id = kwargs.get("category", MISSING)
        channels: list[GuildChannel]
        if parent_id not in (MISSING, None):
            parent_id = parent_id.id
            channels = [
                ch
                for ch in self.guild.channels
                if ch._sorting_bucket == bucket and ch.category_id == parent_id
            ]
        else:
            channels = [
                ch
                for ch in self.guild.channels
                if ch._sorting_bucket == bucket and ch.category_id == self.category_id
            ]

        channels.sort(key=lambda c: (c.position, c.id))

        try:
            # Try to remove ourselves from the channel list
            channels.remove(self)
        except ValueError:
            # If we're not there then it's probably due to not being in the category
            pass

        index = None
        if beginning:
            index = 0
        elif end:
            index = len(channels)
        elif before:
            index = next((i for i, c in enumerate(channels) if c.id == before.id), None)
        elif after:
            index = next(
                (i + 1 for i, c in enumerate(channels) if c.id == after.id), None
            )

        if index is None:
            raise InvalidArgument("Could not resolve appropriate move position")

        channels.insert(max((index + offset), 0), self)
        payload = []
        lock_permissions = kwargs.get("sync_permissions", False)
        reason = kwargs.get("reason")
        for index, channel in enumerate(channels):
            d = {"id": channel.id, "position": index}
            if parent_id is not MISSING and channel.id == self.id:
                d.update(parent_id=parent_id, lock_permissions=lock_permissions)
            payload.append(d)

        await self._state.http.bulk_channel_update(
            self.guild.id, payload, reason=reason
        )

    async def create_invite(
        self,
        *,
        reason: str | None = None,
        max_age: int = 0,
        max_uses: int = 0,
        temporary: bool = False,
        unique: bool = True,
        target_event: ScheduledEvent | None = None,
        target_type: InviteTarget | None = None,
        target_user: User | None = None,
        target_application_id: int | None = None,
    ) -> Invite:
        """|coro|

        Creates an instant invite from a text or voice channel.

        You must have the :attr:`~discord.Permissions.create_instant_invite` permission to
        do this.

        Parameters
        ----------
        max_age: :class:`int`
            How long the invite should last in seconds. If it's 0 then the invite
            doesn't expire. Defaults to ``0``.
        max_uses: :class:`int`
            How many uses the invite could be used for. If it's 0 then there
            are unlimited uses. Defaults to ``0``.
        temporary: :class:`bool`
            Denotes that the invite grants temporary membership
            (i.e. they get kicked after they disconnect). Defaults to ``False``.
        unique: :class:`bool`
            Indicates if a unique invite URL should be created. Defaults to True.
            If this is set to ``False`` then it will return a previously created
            invite.
        reason: Optional[:class:`str`]
            The reason for creating this invite. Shows up on the audit log.
        target_type: Optional[:class:`.InviteTarget`]
            The type of target for the voice channel invite, if any.

            .. versionadded:: 2.0

        target_user: Optional[:class:`User`]
            The user whose stream to display for this invite, required if `target_type` is `TargetType.stream`.
            The user must be streaming in the channel.

            .. versionadded:: 2.0

        target_application_id: Optional[:class:`int`]
            The id of the embedded application for the invite, required if `target_type` is
            `TargetType.embedded_application`.

            .. versionadded:: 2.0

        target_event: Optional[:class:`.ScheduledEvent`]
            The scheduled event object to link to the event.
            Shortcut to :meth:`.Invite.set_scheduled_event`

            See :meth:`.Invite.set_scheduled_event` for more
            info on event invite linking.

            .. versionadded:: 2.0

        Returns
        -------
        :class:`~discord.Invite`
            The invite that was created.

        Raises
        ------
        ~discord.HTTPException
            Invite creation failed.

        ~discord.NotFound
            The channel that was passed is a category or an invalid channel.
        """

        data = await self._state.http.create_invite(
            self.id,
            reason=reason,
            max_age=max_age,
            max_uses=max_uses,
            temporary=temporary,
            unique=unique,
            target_type=target_type.value if target_type else None,
            target_user_id=target_user.id if target_user else None,
            target_application_id=target_application_id,
        )
        invite = Invite.from_incomplete(data=data, state=self._state)
        if target_event:
            invite.set_scheduled_event(target_event)
        return invite

    async def invites(self) -> list[Invite]:
        """|coro|

        Returns a list of all active instant invites from this channel.

        You must have :attr:`~discord.Permissions.manage_channels` to get this information.

        Returns
        -------
        List[:class:`~discord.Invite`]
            The list of invites that are currently active.

        Raises
        ------
        ~discord.Forbidden
            You do not have proper permissions to get the information.
        ~discord.HTTPException
            An error occurred while fetching the information.
        """

        state = self._state
        data = await state.http.invites_from_channel(self.id)
        guild = self.guild
        return [
            Invite(state=state, data=invite, channel=self, guild=guild)
            for invite in data
        ]


class Messageable:
    """An ABC that details the common operations on a model that can send messages.

    The following implement this ABC:

    - :class:`~discord.TextChannel`
    - :class:`~discord.VoiceChannel`
    - :class:`~discord.StageChannel`
    - :class:`~discord.DMChannel`
    - :class:`~discord.GroupChannel`
    - :class:`~discord.User`
    - :class:`~discord.Member`
    - :class:`~discord.ext.commands.Context`
    - :class:`~discord.Thread`
    - :class:`~discord.ApplicationContext`
    """

    __slots__ = ()
    _state: ConnectionState

    async def _get_channel(self) -> MessageableChannel:
        raise NotImplementedError

    @overload
    async def send(
        self,
        content: str | None = ...,
        *,
        tts: bool = ...,
        embed: Embed = ...,
        file: File = ...,
        stickers: Sequence[GuildSticker | StickerItem] = ...,
        delete_after: float = ...,
        nonce: int | str = ...,
        enforce_nonce: bool = ...,
        allowed_mentions: AllowedMentions = ...,
        reference: Message | MessageReference | PartialMessage = ...,
        mention_author: bool = ...,
        view: View = ...,
        poll: Poll = ...,
        suppress: bool = ...,
        silent: bool = ...,
    ) -> Message: ...

    @overload
    async def send(
        self,
        content: str | None = ...,
        *,
        tts: bool = ...,
        embed: Embed = ...,
        files: list[File] = ...,
        stickers: Sequence[GuildSticker | StickerItem] = ...,
        delete_after: float = ...,
        nonce: int | str = ...,
        enforce_nonce: bool = ...,
        allowed_mentions: AllowedMentions = ...,
        reference: Message | MessageReference | PartialMessage = ...,
        mention_author: bool = ...,
        view: View = ...,
        poll: Poll = ...,
        suppress: bool = ...,
        silent: bool = ...,
    ) -> Message: ...

    @overload
    async def send(
        self,
        content: str | None = ...,
        *,
        tts: bool = ...,
        embeds: list[Embed] = ...,
        file: File = ...,
        stickers: Sequence[GuildSticker | StickerItem] = ...,
        delete_after: float = ...,
        nonce: int | str = ...,
        enforce_nonce: bool = ...,
        allowed_mentions: AllowedMentions = ...,
        reference: Message | MessageReference | PartialMessage = ...,
        mention_author: bool = ...,
        view: View = ...,
        poll: Poll = ...,
        suppress: bool = ...,
        silent: bool = ...,
    ) -> Message: ...

    @overload
    async def send(
        self,
        content: str | None = ...,
        *,
        tts: bool = ...,
        embeds: list[Embed] = ...,
        files: list[File] = ...,
        stickers: Sequence[GuildSticker | StickerItem] = ...,
        delete_after: float = ...,
        nonce: int | str = ...,
        enforce_nonce: bool = ...,
        allowed_mentions: AllowedMentions = ...,
        reference: Message | MessageReference | PartialMessage = ...,
        mention_author: bool = ...,
        view: View = ...,
        poll: Poll = ...,
        suppress: bool = ...,
        silent: bool = ...,
    ) -> Message: ...

    async def send(
        self,
        content=None,
        *,
        tts=None,
        embed=None,
        embeds=None,
        file=None,
        files=None,
        stickers=None,
        delete_after=None,
        nonce=None,
        enforce_nonce=None,
        allowed_mentions=None,
        reference=None,
        mention_author=None,
        view=None,
        poll=None,
        suppress=None,
        silent=None,
    ):
        """|coro|

        Sends a message to the destination with the content given.

        The content must be a type that can convert to a string through ``str(content)``.
        If the content is set to ``None`` (the default), then the ``embed`` parameter must
        be provided.

        To upload a single file, the ``file`` parameter should be used with a
        single :class:`~discord.File` object. To upload multiple files, the ``files``
        parameter should be used with a :class:`list` of :class:`~discord.File` objects.
        **Specifying both parameters will lead to an exception**.

        To upload a single embed, the ``embed`` parameter should be used with a
        single :class:`~discord.Embed` object. To upload multiple embeds, the ``embeds``
        parameter should be used with a :class:`list` of :class:`~discord.Embed` objects.
        **Specifying both parameters will lead to an exception**.

        Parameters
        ----------
        content: Optional[:class:`str`]
            The content of the message to send.
        tts: :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        embed: :class:`~discord.Embed`
            The rich embed for the content.
        file: :class:`~discord.File`
            The file to upload.
        files: List[:class:`~discord.File`]
            A list of files to upload. Must be a maximum of 10.
        nonce: Union[:class:`str`, :class:`int`]
            The nonce to use for sending this message. If the message was successfully sent,
            then the message will have a nonce with this value.
        enforce_nonce: Optional[:class:`bool`]
            Whether :attr:`nonce` is enforced to be validated.

            .. versionadded:: 2.5
        delete_after: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent. If the deletion fails,
            then it is silently ignored.
        allowed_mentions: :class:`~discord.AllowedMentions`
            Controls the mentions being processed in this message. If this is
            passed, then the object is merged with :attr:`~discord.Client.allowed_mentions`.
            The merging behaviour only overrides attributes that have been explicitly passed
            to the object, otherwise it uses the attributes set in :attr:`~discord.Client.allowed_mentions`.
            If no object is passed at all then the defaults given by :attr:`~discord.Client.allowed_mentions`
            are used instead.

            .. versionadded:: 1.4

        reference: Union[:class:`~discord.Message`, :class:`~discord.MessageReference`, :class:`~discord.PartialMessage`]
            A reference to the :class:`~discord.Message` being replied to or forwarded. This can be created using
            :meth:`~discord.Message.to_reference`.
            When replying, you can control whether this mentions the author of the referenced message using the
            :attr:`~discord.AllowedMentions.replied_user` attribute of ``allowed_mentions`` or by
            setting ``mention_author``.

            .. versionadded:: 1.6

        mention_author: Optional[:class:`bool`]
            If set, overrides the :attr:`~discord.AllowedMentions.replied_user` attribute of ``allowed_mentions``.

            .. versionadded:: 1.6
        view: :class:`discord.ui.View`
            A Discord UI View to add to the message.
        embeds: List[:class:`~discord.Embed`]
            A list of embeds to upload. Must be a maximum of 10.

            .. versionadded:: 2.0
        stickers: Sequence[Union[:class:`~discord.GuildSticker`, :class:`~discord.StickerItem`]]
            A list of stickers to upload. Must be a maximum of 3.

            .. versionadded:: 2.0
        suppress: :class:`bool`
            Whether to suppress embeds for the message.
        silent: :class:`bool`
            Whether to suppress push and desktop notifications for the message.

            .. versionadded:: 2.4
        poll: :class:`Poll`
            The poll to send.

            .. versionadded:: 2.6

        Returns
        -------
        :class:`~discord.Message`
            The message that was sent.

        Raises
        ------
        ~discord.HTTPException
            Sending the message failed.
        ~discord.Forbidden
            You do not have the proper permissions to send the message.
        ~discord.InvalidArgument
            The ``files`` list is not of the appropriate size,
            you specified both ``file`` and ``files``,
            or you specified both ``embed`` and ``embeds``,
            or the ``reference`` object is not a :class:`~discord.Message`,
            :class:`~discord.MessageReference` or :class:`~discord.PartialMessage`.
        """

        channel = await self._get_channel()
        state = self._state
        content = str(content) if content is not None else None

        if embed is not None and embeds is not None:
            raise InvalidArgument(
                "cannot pass both embed and embeds parameter to send()"
            )

        if embed is not None:
            embed = embed.to_dict()

        elif embeds is not None:
            if len(embeds) > 10:
                raise InvalidArgument(
                    "embeds parameter must be a list of up to 10 elements"
                )
            embeds = [embed.to_dict() for embed in embeds]

        flags = MessageFlags(
            suppress_embeds=bool(suppress),
            suppress_notifications=bool(silent),
        )

        if stickers is not None:
            stickers = [sticker.id for sticker in stickers]

        if allowed_mentions is None:
            allowed_mentions = (
                state.allowed_mentions and state.allowed_mentions.to_dict()
            )
        elif state.allowed_mentions is not None:
            allowed_mentions = state.allowed_mentions.merge(allowed_mentions).to_dict()
        else:
            allowed_mentions = allowed_mentions.to_dict()

        if mention_author is not None:
            allowed_mentions = allowed_mentions or AllowedMentions().to_dict()
            allowed_mentions["replied_user"] = bool(mention_author)

        _reference = None
        if reference is not None:
            try:
                _reference = reference.to_message_reference_dict()
                from .message import MessageReference

                if not isinstance(reference, MessageReference):
                    utils.warn_deprecated(
                        f"Passing {type(reference).__name__} to reference",
                        "MessageReference",
                        "2.7",
                        "3.0",
                    )
            except AttributeError:
                raise InvalidArgument(
                    "reference parameter must be Message, MessageReference, or"
                    " PartialMessage"
                ) from None

        if view:
            if not hasattr(view, "__discord_ui_view__"):
                raise InvalidArgument(
                    f"view parameter must be View not {view.__class__!r}"
                )

            components = view.to_components()
            if view.is_components_v2():
                if embeds or content:
                    raise TypeError(
                        "cannot send embeds or content with a view using v2 component logic"
                    )
                flags.is_components_v2 = True
        else:
            components = None

        if poll:
            poll = poll.to_dict()

        if file is not None and files is not None:
            raise InvalidArgument("cannot pass both file and files parameter to send()")

        if file is not None:
            if not isinstance(file, File):
                raise InvalidArgument("file parameter must be File")
            files = [file]
        elif files is not None:
            if len(files) > 10:
                raise InvalidArgument(
                    "files parameter must be a list of up to 10 elements"
                )
            elif not all(isinstance(file, File) for file in files):
                raise InvalidArgument("files parameter must be a list of File")

        if files is not None:
            flags = flags + MessageFlags(
                is_voice_message=any(isinstance(f, VoiceMessage) for f in files)
            )
            try:
                data = await state.http.send_files(
                    channel.id,
                    files=files,
                    content=content,
                    tts=tts,
                    embed=embed,
                    embeds=embeds,
                    nonce=nonce,
                    enforce_nonce=enforce_nonce,
                    allowed_mentions=allowed_mentions,
                    message_reference=_reference,
                    stickers=stickers,
                    components=components,
                    flags=flags.value,
                    poll=poll,
                )
            finally:
                for f in files:
                    f.close()
        else:
            data = await state.http.send_message(
                channel.id,
                content,
                tts=tts,
                embed=embed,
                embeds=embeds,
                nonce=nonce,
                enforce_nonce=enforce_nonce,
                allowed_mentions=allowed_mentions,
                message_reference=_reference,
                stickers=stickers,
                components=components,
                flags=flags.value,
                poll=poll,
            )

        ret = state.create_message(channel=channel, data=data)
        if view:
            if view.is_dispatchable():
                state.store_view(view, ret.id)
            view.message = ret
            view.refresh(ret.components)

        if delete_after is not None:
            await ret.delete(delay=delete_after)
        return ret

    async def trigger_typing(self) -> None:
        """|coro|

        Triggers a *typing* indicator to the destination.

        *Typing* indicator will go away after 10 seconds, or after a message is sent.
        """

        channel = await self._get_channel()
        await self._state.http.send_typing(channel.id)

    def typing(self) -> Typing:
        """Returns a context manager that allows you to type for an indefinite period of time.

        This is useful for denoting long computations in your bot.

        .. note::

            This is both a regular context manager and an async context manager.
            This means that both ``with`` and ``async with`` work with this.

        Example Usage: ::

            async with channel.typing():
                # simulate something heavy
                await asyncio.sleep(10)

            await channel.send('done!')
        """
        return Typing(self)

    async def fetch_message(self, id: int, /) -> Message:
        """|coro|

        Retrieves a single :class:`~discord.Message` from the destination.

        Parameters
        ----------
        id: :class:`int`
            The message ID to look for.

        Returns
        -------
        :class:`~discord.Message`
            The message asked for.

        Raises
        ------
        ~discord.NotFound
            The specified message was not found.
        ~discord.Forbidden
            You do not have the permissions required to get a message.
        ~discord.HTTPException
            Retrieving the message failed.
        """

        channel = await self._get_channel()
        data = await self._state.http.get_message(channel.id, id)
        return self._state.create_message(channel=channel, data=data)

    async def pins(self) -> list[Message]:
        """|coro|

        Retrieves all messages that are currently pinned in the channel.

        .. note::

            Due to a limitation with the Discord API, the :class:`.Message`
            objects returned by this method do not contain complete
            :attr:`.Message.reactions` data.

        Returns
        -------
        List[:class:`~discord.Message`]
            The messages that are currently pinned.

        Raises
        ------
        ~discord.HTTPException
            Retrieving the pinned messages failed.
        """

        channel = await self._get_channel()
        state = self._state
        data = await state.http.pins_from(channel.id)
        return [state.create_message(channel=channel, data=m) for m in data]

    def can_send(self, *objects) -> bool:
        """Returns a :class:`bool` indicating whether you have the permissions to send the object(s).

        Returns
        -------
        :class:`bool`
            Indicates whether you have the permissions to send the object(s).

        Raises
        ------
        TypeError
            An invalid type has been passed.
        """
        mapping = {
            "Message": "send_messages",
            "Embed": "embed_links",
            "File": "attach_files",
            "GuildEmoji": "use_external_emojis",
            "GuildSticker": "use_external_stickers",
        }
        # Can't use channel = await self._get_channel() since its async
        if hasattr(self, "permissions_for"):
            channel = self
        elif hasattr(self, "channel") and type(self.channel).__name__ not in (
            "DMChannel",
            "GroupChannel",
        ):
            channel = self.channel
        else:
            return True  # Permissions don't exist for User DMs

        objects = (None,) + objects  # Makes sure we check for send_messages first

        for obj in objects:
            try:
                if obj is None:
                    permission = mapping["Message"]
                else:
                    permission = (
                        mapping.get(type(obj).__name__) or mapping[obj.__name__]
                    )

                if type(obj).__name__ == "GuildEmoji":
                    if (
                        obj._to_partial().is_unicode_emoji
                        or obj.guild_id == channel.guild.id
                    ):
                        continue
                elif type(obj).__name__ == "GuildSticker":
                    if obj.guild_id == channel.guild.id:
                        continue

            except (KeyError, AttributeError):
                raise TypeError(f"The object {obj} is of an invalid type.")

            if not getattr(channel.permissions_for(channel.guild.me), permission):
                return False

        return True

    def history(
        self,
        *,
        limit: int | None = 100,
        before: SnowflakeTime | None = None,
        after: SnowflakeTime | None = None,
        around: SnowflakeTime | None = None,
        oldest_first: bool | None = None,
    ) -> HistoryIterator:
        """Returns an :class:`~discord.AsyncIterator` that enables receiving the destination's message history.

        You must have :attr:`~discord.Permissions.read_message_history` permissions to use this.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The number of messages to retrieve.
            If ``None``, retrieves every message in the channel. Note, however,
            that this would make it a slow operation.
        before: Optional[Union[:class:`~discord.abc.Snowflake`, :class:`datetime.datetime`]]
            Retrieve messages before this date or message.
            If a datetime is provided, it is recommended to use a UTC aware datetime.
            If the datetime is naive, it is assumed to be local time.
        after: Optional[Union[:class:`~discord.abc.Snowflake`, :class:`datetime.datetime`]]
            Retrieve messages after this date or message.
            If a datetime is provided, it is recommended to use a UTC aware datetime.
            If the datetime is naive, it is assumed to be local time.
        around: Optional[Union[:class:`~discord.abc.Snowflake`, :class:`datetime.datetime`]]
            Retrieve messages around this date or message.
            If a datetime is provided, it is recommended to use a UTC aware datetime.
            If the datetime is naive, it is assumed to be local time.
            When using this argument, the maximum limit is 101. Note that if the limit is an
            even number, then this will return at most limit + 1 messages.
        oldest_first: Optional[:class:`bool`]
            If set to ``True``, return messages in oldest->newest order. Defaults to ``True`` if
            ``after`` is specified, otherwise ``False``.

        Yields
        ------
        :class:`~discord.Message`
            The message with the message data parsed.

        Raises
        ------
        ~discord.Forbidden
            You do not have permissions to get channel message history.
        ~discord.HTTPException
            The request to get message history failed.

        Examples
        --------

        Usage ::

            counter = 0
            async for message in channel.history(limit=200):
                if message.author == client.user:
                    counter += 1

        Flattening into a list: ::

            messages = await channel.history(limit=123).flatten()
            # messages is now a list of Message...

        All parameters are optional.
        """
        return HistoryIterator(
            self,
            limit=limit,
            before=before,
            after=after,
            around=around,
            oldest_first=oldest_first,
        )


class Connectable(Protocol):
    """An ABC that details the common operations on a channel that can
    connect to a voice server.

    The following implement this ABC:

    - :class:`~discord.VoiceChannel`
    - :class:`~discord.StageChannel`

    Note
    ----
    This ABC is not decorated with :func:`typing.runtime_checkable`, so will fail :func:`isinstance`/:func:`issubclass`
    checks.
    """

    __slots__ = ()
    _state: ConnectionState

    def _get_voice_client_key(self) -> tuple[int, str]:
        raise NotImplementedError

    def _get_voice_state_pair(self) -> tuple[int, int]:
        raise NotImplementedError

    async def connect(
        self,
        *,
        timeout: float = 60.0,
        reconnect: bool = True,
        cls: Callable[[Client, Connectable], T] = VoiceClient,
    ) -> T:
        """|coro|

        Connects to voice and creates a :class:`VoiceClient` to establish
        your connection to the voice server.

        This requires :attr:`Intents.voice_states`.

        Parameters
        ----------
        timeout: :class:`float`
            The timeout in seconds to wait for the voice endpoint.
        reconnect: :class:`bool`
            Whether the bot should automatically attempt
            a reconnect if a part of the handshake fails
            or the gateway goes down.
        cls: Type[:class:`VoiceProtocol`]
            A type that subclasses :class:`~discord.VoiceProtocol` to connect with.
            Defaults to :class:`~discord.VoiceClient`.

        Returns
        -------
        :class:`~discord.VoiceProtocol`
            A voice client that is fully connected to the voice server.

        Raises
        ------
        asyncio.TimeoutError
            Could not connect to the voice channel in time.
        ~discord.ClientException
            You are already connected to a voice channel.
        ~discord.opus.OpusNotLoaded
            The opus library has not been loaded.
        """

        key_id, _ = self._get_voice_client_key()
        state = self._state

        if state._get_voice_client(key_id):
            raise ClientException("Already connected to a voice channel.")

        client = state._get_client()
        voice = cls(client, self)

        if not isinstance(voice, VoiceProtocol):
            raise TypeError("Type must meet VoiceProtocol abstract base class.")

        state._add_voice_client(key_id, voice)

        try:
            await voice.connect(timeout=timeout, reconnect=reconnect)
        except asyncio.TimeoutError:
            try:
                await voice.disconnect(force=True)
            except Exception:
                # we don't care if disconnect failed because connection failed
                pass
            raise  # re-raise

        return voice


class Mentionable:
    # TODO: documentation, methods if needed
    pass
