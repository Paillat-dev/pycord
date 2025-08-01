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

from typing import TYPE_CHECKING, Any, TypeVar

from typing_extensions import Self

from .asset import Asset
from .colour import Colour
from .errors import InvalidArgument
from .flags import RoleFlags
from .mixins import Hashable
from .permissions import Permissions
from .utils import (
    MISSING,
    _bytes_to_base64_data,
    _get_as_snowflake,
    deprecated,
    snowflake_time,
    warn_deprecated,
)

__all__ = ("RoleTags", "Role", "RoleColours")

if TYPE_CHECKING:
    import datetime

    from .guild import Guild
    from .member import Member
    from .state import ConnectionState
    from .types.guild import RolePositionUpdate
    from .types.role import Role as RolePayload
    from .types.role import RoleColours as RoleColoursPayload
    from .types.role import RoleTags as RoleTagPayload


class RoleTags:
    """Represents tags on a role.

    A role tag is a piece of extra information attached to a managed role
    that gives it context for the reason the role is managed.

    While this can be accessed, a useful interface is also provided in the
    :class:`Role` and :class:`Guild` classes as well.

    Role tags are a fairly complex topic, since it's usually hard to determine which role tag combination represents which role type.
    We aim to improve the documentation / introduce new attributes in future.
    For the meantime read `this <https://discord-lib-devs.notion.site/special-roles-role-tags>`_ if you need detailed information about how role tags work.

    .. versionadded:: 1.6

    Attributes
    ----------
    bot_id: Optional[:class:`int`]
        The bot's user ID that manages this role.
    integration_id: Optional[:class:`int`]
        The integration ID that manages the role.
    subscription_listing_id: Optional[:class:`int`]
        The subscription SKU and listing ID of the role.

        .. versionadded:: 2.7
    """

    __slots__ = (
        "bot_id",
        "integration_id",
        "subscription_listing_id",
        "_premium_subscriber",
        "_available_for_purchase",
        "_guild_connections",
    )

    def __init__(self, data: RoleTagPayload):
        self.bot_id: int | None = _get_as_snowflake(data, "bot_id")
        self.integration_id: int | None = _get_as_snowflake(data, "integration_id")
        self.subscription_listing_id: int | None = _get_as_snowflake(
            data, "subscription_listing_id"
        )
        # NOTE: The API returns "null" for each of the following tags if they are True, and omits them if False.
        # However, "null" corresponds to None.
        # This is different from other fields where "null" means "not there".
        # So in this case, a value of None is the same as True.
        # Which means we would need a different sentinel.
        self._premium_subscriber: Any | None = data.get("premium_subscriber", MISSING)
        self._available_for_purchase: Any | None = data.get(
            "available_for_purchase", MISSING
        )
        self._guild_connections: Any | None = data.get("guild_connections", MISSING)

    def is_bot_managed(self) -> bool:
        """Whether the role is associated with a bot."""
        return self.bot_id is not None

    def is_premium_subscriber(self) -> bool:
        """Whether the role is the premium subscriber, AKA "boost", role for the guild."""
        return self._premium_subscriber is None

    def is_integration(self) -> bool:
        """Whether the guild manages the role through some form of
        integrations such as Twitch or through guild subscriptions.
        """
        return self.integration_id is not None

    def is_available_for_purchase(self) -> bool:
        """Whether the role is available for purchase.

        Returns ``True`` if the role is available for purchase, and
        ``False`` if it is not available for purchase or if the role
        is not linked to a guild subscription.

        .. versionadded:: 2.7
        """
        return self._available_for_purchase is None

    def is_guild_connections_role(self) -> bool:
        """Whether the role is a guild connections role.

        .. versionadded:: 2.7
        """
        return self._guild_connections is None

    def __repr__(self) -> str:
        return (
            f"<RoleTags bot_id={self.bot_id} integration_id={self.integration_id} "
            f"subscription_listing_id={self.subscription_listing_id} "
            f"premium_subscriber={self.is_premium_subscriber()} "
            f"available_for_purchase={self.is_available_for_purchase()} "
            f"guild_connections={self.is_guild_connections_role()}>"
        )


R = TypeVar("R", bound="Role")


class RoleColours:
    """Represents a role's gradient colours.

    .. versionadded:: 2.7

    Attributes
    ----------
    primary: :class:`Colour`
        The primary colour of the role.
    secondary: Optional[:class:`Colour`]
        The secondary colour of the role.
    tertiary: Optional[:class:`Colour`]
        The tertiary colour of the role. At the moment, only `16761760` is allowed.
    """

    def __init__(
        self,
        primary: Colour,
        secondary: Colour | None = None,
        tertiary: Colour | None = None,
    ):
        """Initialises a :class:`RoleColours` object.

        .. versionadded:: 2.7

        Parameters
        ----------
        primary: :class:`Colour`
            The primary colour of the role.
        secondary: Optional[:class:`Colour`]
            The secondary colour of the role.
        tertiary: Optional[:class:`Colour`]
            The tertiary colour of the role.
        """
        self.primary: Colour = primary
        self.secondary: Colour | None = secondary
        self.tertiary: Colour | None = tertiary

    @classmethod
    def _from_payload(cls, data: RoleColoursPayload) -> Self:
        primary = Colour(data["primary_color"])
        secondary = (
            Colour(data["secondary_color"]) if data.get("secondary_color") else None
        )
        tertiary = (
            Colour(data["tertiary_color"]) if data.get("tertiary_color") else None
        )
        return cls(primary, secondary, tertiary)

    def _to_dict(self) -> RoleColoursPayload:
        """Converts the role colours to a dictionary."""
        return {
            "primary_color": self.primary.value,
            "secondary_color": self.secondary.value if self.secondary else None,
            "tertiary_color": self.tertiary.value if self.tertiary else None,
        }  # type: ignore

    @classmethod
    def default(cls) -> RoleColours:
        """Returns a default :class:`RoleColours` object with no colours set."""
        return cls(Colour.default(), None, None)

    @classmethod
    def holographic(cls) -> RoleColours:
        """Returns a :class:`RoleColours` that makes the role look holographic.

        Currently holographic roles are only supported with colours 11127295, 16759788, and 16761760.
        """
        return cls(Colour(11127295), Colour(16759788), Colour(16761760))

    @property
    def is_holographic(self) -> bool:
        """Whether the role is holographic.

        Currently roles are holographic when colours are set to 11127295, 16759788, and 16761760.
        """
        return (
            self.primary.value == 11127295
            and self.secondary.value == 16759788
            and self.tertiary.value == 16761760
        )

    def __repr__(self) -> str:
        return (
            f"<RoleColours primary={self.primary!r} "
            f"secondary={self.secondary!r} "
            f"tertiary={self.tertiary!r}>"
        )


class Role(Hashable):
    """Represents a Discord role in a :class:`Guild`.

    .. container:: operations

        .. describe:: x == y

            Checks if two roles are equal.

        .. describe:: x != y

            Checks if two roles are not equal.

        .. describe:: x > y

            Checks if a role is higher than another in the hierarchy.

        .. describe:: x < y

            Checks if a role is lower than another in the hierarchy.

        .. describe:: x >= y

            Checks if a role is higher or equal to another in the hierarchy.

        .. describe:: x <= y

            Checks if a role is lower or equal to another in the hierarchy.

        .. describe:: hash(x)

            Return the role's hash.

        .. describe:: str(x)

            Returns the role's name.

    Attributes
    ----------
    id: :class:`int`
        The ID for the role.
    name: :class:`str`
        The name of the role.
    guild: :class:`Guild`
        The guild the role belongs to.
    hoist: :class:`bool`
         Indicates if the role will be displayed separately from other members.
    position: :class:`int`
        The position of the role. This number is usually positive. The bottom
        role has a position of 0.

        .. warning::

            Multiple roles can have the same position number. As a consequence
            of this, comparing via role position is prone to subtle bugs if
            checking for role hierarchy. The recommended and correct way to
            compare for roles in the hierarchy is using the comparison
            operators on the role objects themselves.

    managed: :class:`bool`
        Indicates if the role is managed by the guild.
        This is true if any of :meth:`Role.is_integration`, :meth:`Role.is_premium_subscriber`,
        :meth:`Role.is_bot_managed` or :meth:`Role.is_guild_connections_role`
        is ``True``.
    mentionable: :class:`bool`
        Indicates if the role can be mentioned by users.
    tags: Optional[:class:`RoleTags`]
        The role tags associated with this role.
    unicode_emoji: Optional[:class:`str`]
        The role's unicode emoji.
        Only available to guilds that contain ``ROLE_ICONS`` in :attr:`Guild.features`.

        .. versionadded:: 2.0

    flags: :class:`RoleFlags`
        Extra attributes of the role.

        .. versionadded:: 2.6

    colours: :class:`RoleColours`
        The role's colours.

        .. versionadded:: 2.7
    """

    __slots__ = (
        "id",
        "name",
        "_permissions",
        "_colour",
        "colours",
        "position",
        "managed",
        "mentionable",
        "hoist",
        "guild",
        "tags",
        "unicode_emoji",
        "_icon",
        "_state",
        "flags",
    )

    def __init__(self, *, guild: Guild, state: ConnectionState, data: RolePayload):
        self.guild: Guild = guild
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self._update(data)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.name!r}>"

    def __lt__(self: R, other: R) -> bool:
        if not isinstance(other, Role) or not isinstance(self, Role):
            return NotImplemented

        if self.guild != other.guild:
            raise RuntimeError("cannot compare roles from two different guilds.")

        # the @everyone role is always the lowest role in hierarchy
        guild_id = self.guild.id
        if self.id == guild_id:
            # everyone_role < everyone_role -> False
            return other.id != guild_id

        if self.position < other.position:
            return True

        if self.position == other.position:
            return int(self.id) > int(other.id)

        return False

    def __le__(self: R, other: R) -> bool:
        r = Role.__lt__(other, self)
        if r is NotImplemented:
            return NotImplemented
        return not r

    def __gt__(self: R, other: R) -> bool:
        return Role.__lt__(other, self)

    def __ge__(self: R, other: R) -> bool:
        r = Role.__lt__(self, other)
        if r is NotImplemented:
            return NotImplemented
        return not r

    def _update(self, data: RolePayload):
        self.name: str = data["name"]
        self._permissions: int = int(data.get("permissions", 0))
        self.position: int = data.get("position", 0)
        self._colour: int = data.get("color", 0)
        self.colours: RoleColours | None = RoleColours._from_payload(data["colors"])
        self.hoist: bool = data.get("hoist", False)
        self.managed: bool = data.get("managed", False)
        self.mentionable: bool = data.get("mentionable", False)
        self._icon: str | None = data.get("icon")
        self.unicode_emoji: str | None = data.get("unicode_emoji")
        self.flags: RoleFlags = RoleFlags._from_value(data.get("flags", 0))
        self.tags: RoleTags | None

        try:
            self.tags = RoleTags(data["tags"])
        except KeyError:
            self.tags = None

    def is_default(self) -> bool:
        """Checks if the role is the default role."""
        return self.guild.id == self.id

    def is_bot_managed(self) -> bool:
        """Whether the role is associated with a bot.

        .. versionadded:: 1.6
        """
        return self.tags is not None and self.tags.is_bot_managed()

    def is_premium_subscriber(self) -> bool:
        """Whether the role is the premium subscriber, AKA "boost", role for the guild.

        .. versionadded:: 1.6
        """
        return self.tags is not None and self.tags.is_premium_subscriber()

    def is_integration(self) -> bool:
        """Whether the guild manages the role through some form of
        integrations such as Twitch or through guild subscriptions.

        .. versionadded:: 1.6
        """
        return self.tags is not None and self.tags.is_integration()

    def is_assignable(self) -> bool:
        """Whether the role is able to be assigned or removed by the bot.

        .. versionadded:: 2.0
        """
        me = self.guild.me
        return (
            not self.is_default()
            and not self.managed
            and (me.top_role > self or me.id == self.guild.owner_id)
        )

    def is_available_for_purchase(self) -> bool:
        """Whether the role is available for purchase.

        Returns ``True`` if the role is available for purchase, and
        ``False`` if it is not available for purchase or if the
        role is not linked to a guild subscription.

        .. versionadded:: 2.7
        """
        return self.tags is not None and self.tags.is_available_for_purchase()

    def is_guild_connections_role(self) -> bool:
        """Whether the role is a guild connections role.

        .. versionadded:: 2.7
        """
        return self.tags is not None and self.tags.is_guild_connections_role()

    @property
    def permissions(self) -> Permissions:
        """Returns the role's permissions."""
        return Permissions(self._permissions)

    @property
    @deprecated("colours.primary", "2.7")
    def colour(self) -> Colour:
        """Returns the role colour. Equivalent to :attr:`colours.primary`.
        An alias exists under ``color``.

        .. versionchanged:: 2.7
        """
        return self.colours.primary

    @property
    @deprecated("colors.primary", "2.7")
    def color(self) -> Colour:
        """Returns the role's primary color. Equivalent to :attr:`colors.primary`.
        An alias exists under ``colour``.

        .. versionchanged:: 2.7
        """
        return self.colours.primary

    @property
    def colors(self) -> RoleColours:
        """Returns the role's colours. Equivalent to :attr:`colours`.

        .. versionadded:: 2.7
        """
        return self.colours

    @property
    def created_at(self) -> datetime.datetime:
        """Returns the role's creation time in UTC."""
        return snowflake_time(self.id)

    @property
    def mention(self) -> str:
        """Returns a string that allows you to mention a role."""
        return f"<@&{self.id}>"

    @property
    def members(self) -> list[Member]:
        """Returns all the members with this role."""
        all_members = self.guild.members
        if self.is_default():
            return all_members

        role_id = self.id
        return [member for member in all_members if member._roles.has(role_id)]

    @property
    def icon(self) -> Asset | None:
        """Returns the role's icon asset, if available.

        .. versionadded:: 2.0
        """
        if self._icon is None:
            return None

        return Asset._from_icon(self._state, self.id, self._icon, "role")

    async def _move(self, position: int, reason: str | None) -> None:
        if position <= 0:
            raise InvalidArgument("Cannot move role to position 0 or below")

        if self.is_default():
            raise InvalidArgument("Cannot move default role")

        if self.position == position:
            return  # Save discord the extra request.

        http = self._state.http

        change_range = range(
            min(self.position, position), max(self.position, position) + 1
        )
        roles = [
            r.id
            for r in self.guild.roles[1:]
            if r.position in change_range and r.id != self.id
        ]

        if self.position > position:
            roles.insert(0, self.id)
        else:
            roles.append(self.id)

        payload: list[RolePositionUpdate] = [
            {"id": z[0], "position": z[1]} for z in zip(roles, change_range)
        ]
        await http.move_role_position(self.guild.id, payload, reason=reason)

    async def edit(
        self,
        *,
        name: str = MISSING,
        permissions: Permissions = MISSING,
        colour: Colour | int = MISSING,
        color: Colour | int = MISSING,
        colours: RoleColours | None = MISSING,
        colors: RoleColours | None = MISSING,
        holographic: bool = MISSING,
        hoist: bool = MISSING,
        mentionable: bool = MISSING,
        position: int = MISSING,
        reason: str | None = MISSING,
        icon: bytes | None = MISSING,
        unicode_emoji: str | None = MISSING,
    ) -> Role:
        """|coro|

        Edits the role.

        You must have the :attr:`~Permissions.manage_roles` permission to
        use this.

        All fields are optional.

        .. versionchanged:: 1.4
            Can now pass ``int`` to ``colour`` keyword-only parameter.

        .. versionchanged:: 2.0
            Edits are no longer in-place, the newly edited role is returned instead.
            Added ``icon`` and ``unicode_emoji``.

        Parameters
        ----------
        name: :class:`str`
            The new role name to change to.
        permissions: :class:`Permissions`
            The new permissions to change to.
        colour: Union[:class:`Colour`, :class:`int`]
            The new colour to change to. (aliased to color as well)
        hoist: :class:`bool`
            Indicates if the role should be shown separately in the member list.
        mentionable: :class:`bool`
            Indicates if the role should be mentionable by others.
        position: :class:`int`
            The new role's position. This must be below your top role's
            position, or it will fail.
        reason: Optional[:class:`str`]
            The reason for editing this role. Shows up on the audit log.
        icon: Optional[:class:`bytes`]
            A :term:`py:bytes-like object` representing the icon. Only PNG/JPEG/WebP is supported.
            If this argument is passed, ``unicode_emoji`` is set to None.
            Only available to guilds that contain ``ROLE_ICONS`` in :attr:`Guild.features`.
            Could be ``None`` to denote removal of the icon.
        unicode_emoji: Optional[:class:`str`]
            The role's unicode emoji. If this argument is passed, ``icon`` is set to None.
            Only available to guilds that contain ``ROLE_ICONS`` in :attr:`Guild.features`.

        Returns
        -------
        :class:`Role`
            The newly edited role.

        Raises
        ------
        Forbidden
            You do not have permissions to change the role.
        HTTPException
            Editing the role failed.
        InvalidArgument
            An invalid position was given or the default
            role was asked to be moved.
        """
        if position is not MISSING:
            await self._move(position, reason=reason)

        payload: dict[str, Any] = {}
        if color is not MISSING:
            colour = color

        if colors is not MISSING:
            colours = colors

        if colour is not MISSING:
            warn_deprecated("colour", "colours", "2.7")
            if isinstance(colour, int):
                colour = Colour(colour)
            colours = RoleColours(primary=colour)
        if holographic:
            colours = RoleColours.holographic()
        if colours is not MISSING:
            if not isinstance(colours, RoleColours):
                raise InvalidArgument("colours must be a RoleColours object")
            if "ENHANCED_ROLE_COLORS" not in self.guild.features:
                colours.secondary = None
                colours.tertiary = None

            payload["colors"] = colours._to_dict()

        if name is not MISSING:
            payload["name"] = name

        if permissions is not MISSING:
            payload["permissions"] = permissions.value

        if hoist is not MISSING:
            payload["hoist"] = hoist

        if mentionable is not MISSING:
            payload["mentionable"] = mentionable

        if icon is not MISSING:
            if icon is None:
                payload["icon"] = None
            else:
                payload["icon"] = _bytes_to_base64_data(icon)
                payload["unicode_emoji"] = None

        if unicode_emoji is not MISSING:
            payload["unicode_emoji"] = unicode_emoji
            payload["icon"] = None

        data = await self._state.http.edit_role(
            self.guild.id, self.id, reason=reason, **payload
        )
        return Role(guild=self.guild, data=data, state=self._state)

    async def delete(self, *, reason: str | None = None) -> None:
        """|coro|

        Deletes the role.

        You must have the :attr:`~Permissions.manage_roles` permission to
        use this.

        Parameters
        ----------
        reason: Optional[:class:`str`]
            The reason for deleting this role. Shows up on the audit log.

        Raises
        ------
        Forbidden
            You do not have permissions to delete the role.
        HTTPException
            Deleting the role failed.
        """

        await self._state.http.delete_role(self.guild.id, self.id, reason=reason)
