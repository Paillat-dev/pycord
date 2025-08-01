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
import logging
import signal
import sys
import traceback
from types import TracebackType
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Generator, Sequence, TypeVar

import aiohttp

from . import utils
from .activity import ActivityTypes, BaseActivity, create_activity
from .appinfo import AppInfo, PartialAppInfo
from .application_role_connection import ApplicationRoleConnectionMetadata
from .backoff import ExponentialBackoff
from .channel import PartialMessageable, _threaded_channel_factory
from .emoji import AppEmoji, GuildEmoji
from .enums import ChannelType, Status
from .errors import *
from .flags import ApplicationFlags, Intents
from .gateway import *
from .guild import Guild
from .http import HTTPClient
from .invite import Invite
from .iterators import EntitlementIterator, GuildIterator
from .mentions import AllowedMentions
from .monetization import SKU, Entitlement
from .object import Object
from .stage_instance import StageInstance
from .state import ConnectionState
from .sticker import GuildSticker, StandardSticker, StickerPack, _sticker_factory
from .template import Template
from .threads import Thread
from .ui.view import View
from .user import ClientUser, User
from .utils import MISSING
from .voice_client import VoiceClient
from .webhook import Webhook
from .widget import Widget

if TYPE_CHECKING:
    from .abc import GuildChannel, PrivateChannel, Snowflake, SnowflakeTime
    from .channel import DMChannel
    from .interaction import Interaction
    from .member import Member
    from .message import Message
    from .poll import Poll
    from .ui.item import Item
    from .voice_client import VoiceProtocol

__all__ = ("Client",)

Coro = TypeVar("Coro", bound=Callable[..., Coroutine[Any, Any, Any]])


_log = logging.getLogger(__name__)


def _cancel_tasks(loop: asyncio.AbstractEventLoop) -> None:
    tasks = {t for t in asyncio.all_tasks(loop=loop) if not t.done()}

    if not tasks:
        return

    _log.info("Cleaning up after %d tasks.", len(tasks))
    for task in tasks:
        task.cancel()

    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    _log.info("All tasks finished cancelling.")

    for task in tasks:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "Unhandled exception during Client.run shutdown.",
                    "exception": task.exception(),
                    "task": task,
                }
            )


def _cleanup_loop(loop: asyncio.AbstractEventLoop) -> None:
    try:
        _cancel_tasks(loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        _log.info("Closing the event loop.")
        loop.close()


class Client:
    r"""Represents a client connection that connects to Discord.
    This class is used to interact with the Discord WebSocket and API.

    A number of options can be passed to the :class:`Client`.

    Parameters
    -----------
    max_messages: Optional[:class:`int`]
        The maximum number of messages to store in the internal message cache.
        This defaults to ``1000``. Passing in ``None`` disables the message cache.

        .. versionchanged:: 1.3
            Allow disabling the message cache and change the default size to ``1000``.
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The :class:`asyncio.AbstractEventLoop` to use for asynchronous operations.
        Defaults to ``None``, in which case the default event loop is used via
        :func:`asyncio.get_event_loop()`.
    connector: Optional[:class:`aiohttp.BaseConnector`]
        The connector to use for connection pooling.
    proxy: Optional[:class:`str`]
        Proxy URL.
    proxy_auth: Optional[:class:`aiohttp.BasicAuth`]
        An object that represents proxy HTTP Basic Authorization.
    shard_id: Optional[:class:`int`]
        Integer starting at ``0`` and less than :attr:`.shard_count`.
    shard_count: Optional[:class:`int`]
        The total number of shards.
    application_id: :class:`int`
        The client's application ID.
    intents: :class:`Intents`
        The intents that you want to enable for the session. This is a way of
        disabling and enabling certain gateway events from triggering and being sent.
        If not given, defaults to a regularly constructed :class:`Intents` class.

        .. versionadded:: 1.5
    member_cache_flags: :class:`MemberCacheFlags`
        Allows for finer control over how the library caches members.
        If not given, defaults to cache as much as possible with the
        currently selected intents.

        .. versionadded:: 1.5
    chunk_guilds_at_startup: :class:`bool`
        Indicates if :func:`.on_ready` should be delayed to chunk all guilds
        at start-up if necessary. This operation is incredibly slow for large
        amounts of guilds. The default is ``True`` if :attr:`Intents.members`
        is ``True``.

        .. versionadded:: 1.5
    status: Optional[:class:`.Status`]
        A status to start your presence with upon logging on to Discord.
    activity: Optional[:class:`.BaseActivity`]
        An activity to start your presence with upon logging on to Discord.
    allowed_mentions: Optional[:class:`AllowedMentions`]
        Control how the client handles mentions by default on every message sent.

        .. versionadded:: 1.4
    heartbeat_timeout: :class:`float`
        The maximum numbers of seconds before timing out and restarting the
        WebSocket in the case of not receiving a HEARTBEAT_ACK. Useful if
        processing the initial packets take too long to the point of disconnecting
        you. The default timeout is 60 seconds.
    guild_ready_timeout: :class:`float`
        The maximum number of seconds to wait for the GUILD_CREATE stream to end before
        preparing the member cache and firing READY. The default timeout is 2 seconds.

        .. versionadded:: 1.4
    assume_unsync_clock: :class:`bool`
        Whether to assume the system clock is unsynced. This applies to the ratelimit handling
        code. If this is set to ``True``, the default, then the library uses the time to reset
        a rate limit bucket given by Discord. If this is ``False`` then your system clock is
        used to calculate how long to sleep for. If this is set to ``False`` it is recommended to
        sync your system clock to Google's NTP server.

        .. versionadded:: 1.3
    enable_debug_events: :class:`bool`
        Whether to enable events that are useful only for debugging gateway related information.

        Right now this involves :func:`on_socket_raw_receive` and :func:`on_socket_raw_send`. If
        this is ``False`` then those events will not be dispatched (due to performance considerations).
        To enable these events, this must be set to ``True``. Defaults to ``False``.

        .. versionadded:: 2.0
    cache_app_emojis: :class:`bool`
        Whether to automatically fetch and cache the application's emojis on startup and when fetching. Defaults to ``False``.

        .. warning::

            There are no events related to application emojis - if any are created/deleted on the
            Developer Dashboard while the client is running, the cache will not be updated until you manually
            run :func:`fetch_emojis`.

        .. versionadded:: 2.7

    Attributes
    -----------
    ws
        The WebSocket gateway the client is currently connected to. Could be ``None``.
    loop: :class:`asyncio.AbstractEventLoop`
        The event loop that the client uses for asynchronous operations.
    """

    def __init__(
        self,
        *,
        loop: asyncio.AbstractEventLoop | None = None,
        **options: Any,
    ):
        # self.ws is set in the connect method
        self.ws: DiscordWebSocket = None  # type: ignore
        self.loop: asyncio.AbstractEventLoop = (
            asyncio.get_event_loop() if loop is None else loop
        )
        self._listeners: dict[str, list[tuple[asyncio.Future, Callable[..., bool]]]] = (
            {}
        )
        self.shard_id: int | None = options.get("shard_id")
        self.shard_count: int | None = options.get("shard_count")

        connector: aiohttp.BaseConnector | None = options.pop("connector", None)
        proxy: str | None = options.pop("proxy", None)
        proxy_auth: aiohttp.BasicAuth | None = options.pop("proxy_auth", None)
        unsync_clock: bool = options.pop("assume_unsync_clock", True)
        self.http: HTTPClient = HTTPClient(
            connector,
            proxy=proxy,
            proxy_auth=proxy_auth,
            unsync_clock=unsync_clock,
            loop=self.loop,
        )

        self._handlers: dict[str, Callable] = {"ready": self._handle_ready}

        self._hooks: dict[str, Callable] = {
            "before_identify": self._call_before_identify_hook
        }

        self._enable_debug_events: bool = options.pop("enable_debug_events", False)
        self._connection: ConnectionState = self._get_state(**options)
        self._connection.shard_count = self.shard_count
        self._closed: bool = False
        self._ready: asyncio.Event = asyncio.Event()
        self._connection._get_websocket = self._get_websocket
        self._connection._get_client = lambda: self
        self._event_handlers: dict[str, list[Coro]] = {}

        if VoiceClient.warn_nacl:
            VoiceClient.warn_nacl = False
            _log.warning("PyNaCl is not installed, voice will NOT be supported")

        # Used to hard-reference tasks so they don't get garbage collected (discarded with done_callbacks)
        self._tasks = set()

    async def __aenter__(self) -> Client:
        loop = asyncio.get_running_loop()
        self.loop = loop
        self.http.loop = loop
        self._connection.loop = loop

        self._ready = asyncio.Event()

        return self

    async def __aexit__(
        self,
        exc_t: BaseException | None,
        exc_v: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if not self.is_closed():
            await self.close()

    # internals

    def _get_websocket(
        self, guild_id: int | None = None, *, shard_id: int | None = None
    ) -> DiscordWebSocket:
        return self.ws

    def _get_state(self, **options: Any) -> ConnectionState:
        return ConnectionState(
            dispatch=self.dispatch,
            handlers=self._handlers,
            hooks=self._hooks,
            http=self.http,
            loop=self.loop,
            **options,
        )

    def _handle_ready(self) -> None:
        self._ready.set()

    @property
    def latency(self) -> float:
        """Measures latency between a HEARTBEAT and a HEARTBEAT_ACK in seconds. If no websocket
        is present, this returns ``nan``, and if no heartbeat has been received yet, this returns ``float('inf')``.

        This could be referred to as the Discord WebSocket protocol latency.
        """
        ws = self.ws
        return float("nan") if not ws else ws.latency

    def is_ws_ratelimited(self) -> bool:
        """Whether the WebSocket is currently rate limited.

        This can be useful to know when deciding whether you should query members
        using HTTP or via the gateway.

        .. versionadded:: 1.6
        """
        if self.ws:
            return self.ws.is_ratelimited()
        return False

    @property
    def user(self) -> ClientUser | None:
        """Represents the connected client. ``None`` if not logged in."""
        return self._connection.user

    @property
    def guilds(self) -> list[Guild]:
        """The guilds that the connected client is a member of."""
        return self._connection.guilds

    @property
    def emojis(self) -> list[GuildEmoji | AppEmoji]:
        """The emojis that the connected client has.

        .. note::

            This only includes the application's emojis if `cache_app_emojis` is ``True``.
        """
        return self._connection.emojis

    @property
    def guild_emojis(self) -> list[GuildEmoji]:
        """The :class:`~discord.GuildEmoji` that the connected client has."""
        return [e for e in self.emojis if isinstance(e, GuildEmoji)]

    @property
    def app_emojis(self) -> list[AppEmoji]:
        """The :class:`~discord.AppEmoji` that the connected client has.

        .. note::

            This is only available if `cache_app_emojis` is ``True``.
        """
        return [e for e in self.emojis if isinstance(e, AppEmoji)]

    @property
    def stickers(self) -> list[GuildSticker]:
        """The stickers that the connected client has.

        .. versionadded:: 2.0
        """
        return self._connection.stickers

    @property
    def polls(self) -> list[Poll]:
        """The polls that the connected client has.

        .. versionadded:: 2.6
        """
        return self._connection.polls

    @property
    def cached_messages(self) -> Sequence[Message]:
        """Read-only list of messages the connected client has cached.

        .. versionadded:: 1.1
        """
        return utils.SequenceProxy(self._connection._messages or [])

    @property
    def private_channels(self) -> list[PrivateChannel]:
        """The private channels that the connected client is participating on.

        .. note::

            This returns only up to 128 most recent private channels due to an internal working
            on how Discord deals with private channels.
        """
        return self._connection.private_channels

    @property
    def voice_clients(self) -> list[VoiceProtocol]:
        """Represents a list of voice connections.

        These are usually :class:`.VoiceClient` instances.
        """
        return self._connection.voice_clients

    @property
    def application_id(self) -> int | None:
        """The client's application ID.

        If this is not passed via ``__init__`` then this is retrieved
        through the gateway when an event contains the data. Usually
        after :func:`~discord.on_connect` is called.

        .. versionadded:: 2.0
        """
        return self._connection.application_id

    @property
    def application_flags(self) -> ApplicationFlags:
        """The client's application flags.

        .. versionadded:: 2.0
        """
        return self._connection.application_flags  # type: ignore

    def is_ready(self) -> bool:
        """Specifies if the client's internal cache is ready for use."""
        return self._ready.is_set()

    async def _run_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception:
            try:
                await self.on_error(event_name, *args, **kwargs)
            except asyncio.CancelledError:
                pass

    def _schedule_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> asyncio.Task:
        wrapped = self._run_event(coro, event_name, *args, **kwargs)

        # Schedule task and store in set to avoid task garbage collection
        task = asyncio.create_task(wrapped, name=f"pycord: {event_name}")
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> None:
        _log.debug("Dispatching event %s", event)
        method = f"on_{event}"

        listeners = self._listeners.get(event)
        if listeners:
            removed = []
            for i, (future, condition) in enumerate(listeners):
                if future.cancelled():
                    removed.append(i)
                    continue

                try:
                    result = condition(*args)
                except Exception as exc:
                    future.set_exception(exc)
                    removed.append(i)
                else:
                    if result:
                        if len(args) == 0:
                            future.set_result(None)
                        elif len(args) == 1:
                            future.set_result(args[0])
                        else:
                            future.set_result(args)
                        removed.append(i)

            if len(removed) == len(listeners):
                self._listeners.pop(event)
            else:
                for idx in reversed(removed):
                    del listeners[idx]

        # Schedule the main handler registered with @event
        try:
            coro = getattr(self, method)
        except AttributeError:
            pass
        else:
            self._schedule_event(coro, method, *args, **kwargs)

        # collect the once listeners as removing them from the list
        # while iterating over it causes issues
        once_listeners = []

        # Schedule additional handlers registered with @listen
        for coro in self._event_handlers.get(method, []):
            self._schedule_event(coro, method, *args, **kwargs)

            try:
                if coro._once:  # added using @listen()
                    once_listeners.append(coro)

            except AttributeError:  # added using @Cog.add_listener()
                # https://github.com/Pycord-Development/pycord/pull/1989
                # Although methods are similar to functions, attributes can't be added to them.
                # This means that we can't add the `_once` attribute in the `add_listener` method
                # and can only be added using the `@listen` decorator.

                continue

        # remove the once listeners
        for coro in once_listeners:
            self._event_handlers[method].remove(coro)

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        """|coro|

        The default error handler provided by the client.

        By default, this prints to :data:`sys.stderr` however it could be
        overridden to have a different implementation.
        Check :func:`~discord.on_error` for more details.
        """
        print(f"Ignoring exception in {event_method}", file=sys.stderr)
        traceback.print_exc()

    async def on_view_error(
        self, error: Exception, item: Item, interaction: Interaction
    ) -> None:
        """|coro|

        The default view error handler provided by the client.

        This only fires for a view if you did not define its :func:`~discord.ui.View.on_error`.
        """

        print(
            f"Ignoring exception in view {interaction.view} for item {item}:",
            file=sys.stderr,
        )
        traceback.print_exception(
            error.__class__, error, error.__traceback__, file=sys.stderr
        )

    async def on_modal_error(self, error: Exception, interaction: Interaction) -> None:
        """|coro|

        The default modal error handler provided by the client.
        The default implementation prints the traceback to stderr.

        This only fires for a modal if you did not define its :func:`~discord.ui.Modal.on_error`.
        """

        print(f"Ignoring exception in modal {interaction.modal}:", file=sys.stderr)
        traceback.print_exception(
            error.__class__, error, error.__traceback__, file=sys.stderr
        )

    # hooks

    async def _call_before_identify_hook(
        self, shard_id: int | None, *, initial: bool = False
    ) -> None:
        # This hook is an internal hook that actually calls the public one.
        # It allows the library to have its own hook without stepping on the
        # toes of those who need to override their own hook.
        await self.before_identify_hook(shard_id, initial=initial)

    async def before_identify_hook(
        self, shard_id: int | None, *, initial: bool = False
    ) -> None:
        """|coro|

        A hook that is called before IDENTIFYing a session. This is useful
        if you wish to have more control over the synchronization of multiple
        IDENTIFYing clients.

        The default implementation sleeps for 5 seconds.

        .. versionadded:: 1.4

        Parameters
        ----------
        shard_id: :class:`int`
            The shard ID that requested being IDENTIFY'd
        initial: :class:`bool`
            Whether this IDENTIFY is the first initial IDENTIFY.
        """

        if not initial:
            await asyncio.sleep(5.0)

    # login state management

    async def login(self, token: str) -> None:
        """|coro|

        Logs in the client with the specified credentials.

        Parameters
        ----------
        token: :class:`str`
            The authentication token. Do not prefix this token with
            anything as the library will do it for you.

        Raises
        ------
        TypeError
            The token was in invalid type.
        :exc:`LoginFailure`
            The wrong credentials are passed.
        :exc:`HTTPException`
            An unknown HTTP related error occurred,
            usually when it isn't 200 or the known incorrect credentials
            passing status code.
        """
        if not isinstance(token, str):
            raise TypeError(
                f"token must be of type str, not {token.__class__.__name__}"
            )

        _log.info("logging in using static token")

        data = await self.http.static_login(token.strip())
        self._connection.user = ClientUser(state=self._connection, data=data)

    async def connect(self, *, reconnect: bool = True) -> None:
        """|coro|

        Creates a WebSocket connection and lets the WebSocket listen
        to messages from Discord. This is a loop that runs the entire
        event system and miscellaneous aspects of the library. Control
        is not resumed until the WebSocket connection is terminated.

        Parameters
        ----------
        reconnect: :class:`bool`
            If we should attempt reconnecting, either due to internet
            failure or a specific failure on Discord's part. Certain
            disconnects that lead to bad state will not be handled (such as
            invalid sharding payloads or bad tokens).

        Raises
        ------
        :exc:`GatewayNotFound`
            The gateway to connect to Discord is not found. Usually if this
            is thrown then there is a Discord API outage.
        :exc:`ConnectionClosed`
            The WebSocket connection has been terminated.
        """

        backoff = ExponentialBackoff()
        ws_params = {
            "initial": True,
            "shard_id": self.shard_id,
        }
        while not self.is_closed():
            try:
                coro = DiscordWebSocket.from_client(self, **ws_params)
                self.ws = await asyncio.wait_for(coro, timeout=60.0)
                ws_params["initial"] = False
                while True:
                    await self.ws.poll_event()
            except ReconnectWebSocket as e:
                _log.info("Got a request to %s the websocket.", e.op)
                self.dispatch("disconnect")
                ws_params.update(
                    sequence=self.ws.sequence,
                    resume=e.resume,
                    session=self.ws.session_id,
                )
                continue
            except (
                OSError,
                HTTPException,
                GatewayNotFound,
                ConnectionClosed,
                aiohttp.ClientError,
                asyncio.TimeoutError,
            ) as exc:
                self.dispatch("disconnect")
                if not reconnect:
                    await self.close()
                    if isinstance(exc, ConnectionClosed) and exc.code == 1000:
                        # clean close, don't re-raise this
                        return
                    raise

                if self.is_closed():
                    return

                # If we get connection reset by peer then try to RESUME
                if isinstance(exc, OSError) and exc.errno in (54, 10054):
                    ws_params.update(
                        sequence=self.ws.sequence,
                        initial=False,
                        resume=True,
                        session=self.ws.session_id,
                    )
                    continue

                # We should only get this when an unhandled close code happens,
                # such as a clean disconnect (1000) or a bad state (bad token, no sharding, etc)
                # sometimes, discord sends us 1000 for unknown reasons, so we should reconnect
                # regardless and rely on is_closed instead
                if isinstance(exc, ConnectionClosed):
                    if exc.code == 4014:
                        raise PrivilegedIntentsRequired(exc.shard_id) from None
                    if exc.code != 1000:
                        await self.close()
                        raise

                retry = backoff.delay()
                _log.exception("Attempting a reconnect in %.2fs", retry)
                await asyncio.sleep(retry)
                # Always try to RESUME the connection
                # If the connection is not RESUME-able then the gateway will invalidate the session.
                # This is apparently what the official Discord client does.
                if self.ws is None:
                    continue
                ws_params.update(
                    sequence=self.ws.sequence, resume=True, session=self.ws.session_id
                )

    async def close(self) -> None:
        """|coro|

        Closes the connection to Discord.
        """
        if self._closed:
            return

        await self.http.close()
        self._closed = True

        for voice in self.voice_clients:
            try:
                await voice.disconnect(force=True)
            except Exception:
                # if an error happens during disconnects, disregard it.
                pass

        if self.ws is not None and self.ws.open:
            await self.ws.close(code=1000)

        self._ready.clear()

    def clear(self) -> None:
        """Clears the internal state of the bot.

        After this, the bot can be considered "re-opened", i.e. :meth:`is_closed`
        and :meth:`is_ready` both return ``False`` along with the bot's internal
        cache cleared.
        """
        self._closed = False
        self._ready.clear()
        self._connection.clear()
        self.http.recreate()

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        """|coro|

        A shorthand coroutine for :meth:`login` + :meth:`connect`.

        Raises
        ------
        TypeError
            An unexpected keyword argument was received.
        """
        await self.login(token)
        await self.connect(reconnect=reconnect)

    def run(self, *args: Any, **kwargs: Any) -> None:
        """A blocking call that abstracts away the event loop
        initialisation from you.

        If you want more control over the event loop then this
        function should not be used. Use :meth:`start` coroutine
        or :meth:`connect` + :meth:`login`.

        Roughly Equivalent to: ::

            try:
                loop.run_until_complete(start(*args, **kwargs))
            except KeyboardInterrupt:
                loop.run_until_complete(close())
                # cancel all tasks lingering
            finally:
                loop.close()

        .. warning::

            This function must be the last function to call due to the fact that it
            is blocking. That means that registration of events or anything being
            called after this function call will not execute until it returns.
        """
        loop = self.loop

        try:
            loop.add_signal_handler(signal.SIGINT, loop.stop)
            loop.add_signal_handler(signal.SIGTERM, loop.stop)
        except (NotImplementedError, RuntimeError):
            pass

        async def runner():
            try:
                await self.start(*args, **kwargs)
            finally:
                if not self.is_closed():
                    await self.close()

        def stop_loop_on_completion(f):
            loop.stop()

        future = asyncio.ensure_future(runner(), loop=loop)
        future.add_done_callback(stop_loop_on_completion)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            _log.info("Received signal to terminate bot and event loop.")
        finally:
            future.remove_done_callback(stop_loop_on_completion)
            _log.info("Cleaning up tasks.")
            _cleanup_loop(loop)

        if not future.cancelled():
            try:
                return future.result()
            except KeyboardInterrupt:
                # I am unsure why this gets raised here but suppress it anyway
                return None

    # properties

    def is_closed(self) -> bool:
        """Indicates if the WebSocket connection is closed."""
        return self._closed

    @property
    def activity(self) -> ActivityTypes | None:
        """The activity being used upon logging in.

        Returns
        -------
        Optional[:class:`.BaseActivity`]
        """
        return create_activity(self._connection._activity)

    @activity.setter
    def activity(self, value: ActivityTypes | None) -> None:
        if value is None:
            self._connection._activity = None
        elif isinstance(value, BaseActivity):
            # ConnectionState._activity is typehinted as ActivityPayload, we're passing Dict[str, Any]
            self._connection._activity = value.to_dict()  # type: ignore
        else:
            raise TypeError("activity must derive from BaseActivity.")

    @property
    def status(self) -> Status:
        """The status being used upon logging on to Discord.

        .. versionadded: 2.0
        """
        if self._connection._status in {state.value for state in Status}:
            return Status(self._connection._status)
        return Status.online

    @status.setter
    def status(self, value: Status) -> None:
        if value is Status.offline:
            self._connection._status = "invisible"
        elif isinstance(value, Status):
            self._connection._status = str(value)
        else:
            raise TypeError("status must derive from Status.")

    @property
    def allowed_mentions(self) -> AllowedMentions | None:
        """The allowed mention configuration.

        .. versionadded:: 1.4
        """
        return self._connection.allowed_mentions

    @allowed_mentions.setter
    def allowed_mentions(self, value: AllowedMentions | None) -> None:
        if value is None or isinstance(value, AllowedMentions):
            self._connection.allowed_mentions = value
        else:
            raise TypeError(
                f"allowed_mentions must be AllowedMentions not {value.__class__!r}"
            )

    @property
    def intents(self) -> Intents:
        """The intents configured for this connection.

        .. versionadded:: 1.5
        """
        return self._connection.intents

    # helpers/getters

    @property
    def users(self) -> list[User]:
        """Returns a list of all the users the bot can see."""
        return list(self._connection._users.values())

    async def fetch_application(self, application_id: int, /) -> PartialAppInfo:
        """|coro|
        Retrieves a :class:`.PartialAppInfo` from an application ID.

        Parameters
        ----------
        application_id: :class:`int`
            The application ID to retrieve information from.

        Returns
        -------
        :class:`.PartialAppInfo`
            The application information.

        Raises
        ------
        NotFound
            An application with this ID does not exist.
        HTTPException
            Retrieving the application failed.
        """
        data = await self.http.get_application(application_id)
        return PartialAppInfo(state=self._connection, data=data)

    def get_channel(self, id: int, /) -> GuildChannel | Thread | PrivateChannel | None:
        """Returns a channel or thread with the given ID.

        Parameters
        ----------
        id: :class:`int`
            The ID to search for.

        Returns
        -------
        Optional[Union[:class:`.abc.GuildChannel`, :class:`.Thread`, :class:`.abc.PrivateChannel`]]
            The returned channel or ``None`` if not found.
        """
        return self._connection.get_channel(id)

    def get_message(self, id: int, /) -> Message | None:
        """Returns a message the given ID.

        This is useful if you have a message_id but don't want to do an API call
        to access the message.

        Parameters
        ----------
        id: :class:`int`
            The ID to search for.

        Returns
        -------
        Optional[:class:`.Message`]
            The returned message or ``None`` if not found.
        """
        return self._connection._get_message(id)

    def get_partial_messageable(
        self, id: int, *, type: ChannelType | None = None
    ) -> PartialMessageable:
        """Returns a partial messageable with the given channel ID.

        This is useful if you have a channel_id but don't want to do an API call
        to send messages to it.

        .. versionadded:: 2.0

        Parameters
        ----------
        id: :class:`int`
            The channel ID to create a partial messageable for.
        type: Optional[:class:`.ChannelType`]
            The underlying channel type for the partial messageable.

        Returns
        -------
        :class:`.PartialMessageable`
            The partial messageable
        """
        return PartialMessageable(state=self._connection, id=id, type=type)

    def get_stage_instance(self, id: int, /) -> StageInstance | None:
        """Returns a stage instance with the given stage channel ID.

        .. versionadded:: 2.0

        Parameters
        ----------
        id: :class:`int`
            The ID to search for.

        Returns
        -------
        Optional[:class:`.StageInstance`]
            The stage instance or ``None`` if not found.
        """
        from .channel import StageChannel

        channel = self._connection.get_channel(id)

        if isinstance(channel, StageChannel):
            return channel.instance

    def get_guild(self, id: int, /) -> Guild | None:
        """Returns a guild with the given ID.

        Parameters
        ----------
        id: :class:`int`
            The ID to search for.

        Returns
        -------
        Optional[:class:`.Guild`]
            The guild or ``None`` if not found.
        """
        return self._connection._get_guild(id)

    def get_user(self, id: int, /) -> User | None:
        """Returns a user with the given ID.

        Parameters
        ----------
        id: :class:`int`
            The ID to search for.

        Returns
        -------
        Optional[:class:`~discord.User`]
            The user or ``None`` if not found.
        """
        return self._connection.get_user(id)

    def get_emoji(self, id: int, /) -> GuildEmoji | AppEmoji | None:
        """Returns an emoji with the given ID.

        Parameters
        ----------
        id: :class:`int`
            The ID to search for.

        Returns
        -------
        Optional[:class:`.GuildEmoji` | :class:`.AppEmoji`]
            The custom emoji or ``None`` if not found.
        """
        return self._connection.get_emoji(id)

    def get_sticker(self, id: int, /) -> GuildSticker | None:
        """Returns a guild sticker with the given ID.

        .. versionadded:: 2.0

        .. note::

            To retrieve standard stickers, use :meth:`.fetch_sticker`.
            or :meth:`.fetch_premium_sticker_packs`.

        Returns
        -------
        Optional[:class:`.GuildSticker`]
            The sticker or ``None`` if not found.
        """
        return self._connection.get_sticker(id)

    def get_poll(self, id: int, /) -> Poll | None:
        """Returns a poll attached to the given message ID.

        Parameters
        ----------
        id: :class:`int`
            The message ID of the poll to search for.

        Returns
        -------
        Optional[:class:`.Poll`]
            The poll or ``None`` if not found.
        """
        return self._connection.get_poll(id)

    def get_all_channels(self) -> Generator[GuildChannel]:
        """A generator that retrieves every :class:`.abc.GuildChannel` the client can 'access'.

        This is equivalent to: ::

            for guild in client.guilds:
                for channel in guild.channels:
                    yield channel

        .. note::

            Just because you receive a :class:`.abc.GuildChannel` does not mean that
            you can communicate in said channel. :meth:`.abc.GuildChannel.permissions_for` should
            be used for that.

        Yields
        ------
        :class:`.abc.GuildChannel`
            A channel the client can 'access'.
        """

        for guild in self.guilds:
            yield from guild.channels

    def get_all_members(self) -> Generator[Member]:
        """Returns a generator with every :class:`.Member` the client can see.

        This is equivalent to: ::

            for guild in client.guilds:
                for member in guild.members:
                    yield member

        Yields
        ------
        :class:`.Member`
            A member the client can see.
        """
        for guild in self.guilds:
            yield from guild.members

    async def get_or_fetch_user(self, id: int, /) -> User | None:
        """|coro|

        Looks up a user in the user cache or fetches if not found.

        Parameters
        ----------
        id: :class:`int`
            The ID to search for.

        Returns
        -------
        Optional[:class:`~discord.User`]
            The user or ``None`` if not found.
        """

        return await utils.get_or_fetch(obj=self, attr="user", id=id, default=None)

    # listeners/waiters

    async def wait_until_ready(self) -> None:
        """|coro|

        Waits until the client's internal cache is all ready.
        """
        await self._ready.wait()

    def wait_for(
        self,
        event: str,
        *,
        check: Callable[..., bool] | None = None,
        timeout: float | None = None,
    ) -> Any:
        """|coro|

        Waits for a WebSocket event to be dispatched.

        This could be used to wait for a user to reply to a message,
        or to react to a message, or to edit a message in a self-contained
        way.

        The ``timeout`` parameter is passed onto :func:`asyncio.wait_for`. By default,
        it does not timeout. Note that this does propagate the
        :exc:`asyncio.TimeoutError` for you in case of timeout and is provided for
        ease of use.

        In case the event returns multiple arguments, a :class:`tuple` containing those
        arguments is returned instead. Please check the
        :ref:`documentation <discord-api-events>` for a list of events and their
        parameters.

        This function returns the **first event that meets the requirements**.

        Parameters
        ----------
        event: :class:`str`
            The event name, similar to the :ref:`event reference <discord-api-events>`,
            but without the ``on_`` prefix, to wait for.
        check: Optional[Callable[..., :class:`bool`]]
            A predicate to check what to wait for. The arguments must meet the
            parameters of the event being waited for.
        timeout: Optional[:class:`float`]
            The number of seconds to wait before timing out and raising
            :exc:`asyncio.TimeoutError`.

        Returns
        -------
        Any
            Returns no arguments, a single argument, or a :class:`tuple` of multiple
            arguments that mirrors the parameters passed in the
            :ref:`event reference <discord-api-events>`.

        Raises
        ------
        asyncio.TimeoutError
            Raised if a timeout is provided and reached.

        Examples
        --------

        Waiting for a user reply: ::

            @client.event
            async def on_message(message):
                if message.content.startswith('$greet'):
                    channel = message.channel
                    await channel.send('Say hello!')

                    def check(m):
                        return m.content == 'hello' and m.channel == channel

                    msg = await client.wait_for('message', check=check)
                    await channel.send(f'Hello {msg.author}!')

        Waiting for a thumbs up reaction from the message author: ::

            @client.event
            async def on_message(message):
                if message.content.startswith('$thumb'):
                    channel = message.channel
                    await channel.send('Send me that \N{THUMBS UP SIGN} reaction, mate')

                    def check(reaction, user):
                        return user == message.author and str(reaction.emoji) == '\N{THUMBS UP SIGN}'

                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
                    except asyncio.TimeoutError:
                        await channel.send('\N{THUMBS DOWN SIGN}')
                    else:
                        await channel.send('\N{THUMBS UP SIGN}')
        """

        future = self.loop.create_future()
        if check is None:

            def _check(*args):
                return True

            check = _check

        ev = event.lower()
        try:
            listeners = self._listeners[ev]
        except KeyError:
            listeners = []
            self._listeners[ev] = listeners

        listeners.append((future, check))
        return asyncio.wait_for(future, timeout)

    # event registration
    def add_listener(self, func: Coro, name: str = MISSING) -> None:
        """The non decorator alternative to :meth:`.listen`.

        Parameters
        ----------
        func: :ref:`coroutine <coroutine>`
            The function to call.
        name: :class:`str`
            The name of the event to listen for. Defaults to ``func.__name__``.

        Raises
        ------
        TypeError
            The ``func`` parameter is not a coroutine function.
        ValueError
            The ``name`` (event name) does not start with 'on_'

        Example
        -------

        .. code-block:: python3

            async def on_ready(): pass
            async def my_message(message): pass

            client.add_listener(on_ready)
            client.add_listener(my_message, 'on_message')
        """
        name = func.__name__ if name is MISSING else name

        if not name.startswith("on_"):
            raise ValueError("The 'name' parameter must start with 'on_'")

        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Listeners must be coroutines")

        if name in self._event_handlers:
            self._event_handlers[name].append(func)
        else:
            self._event_handlers[name] = [func]

        _log.debug(
            "%s has successfully been registered as a handler for event %s",
            func.__name__,
            name,
        )

    def remove_listener(self, func: Coro, name: str = MISSING) -> None:
        """Removes a listener from the pool of listeners.

        Parameters
        ----------
        func
            The function that was used as a listener to remove.
        name: :class:`str`
            The name of the event we want to remove. Defaults to
            ``func.__name__``.
        """

        name = func.__name__ if name is MISSING else name

        if name in self._event_handlers:
            try:
                self._event_handlers[name].remove(func)
            except ValueError:
                pass

    def listen(self, name: str = MISSING, once: bool = False) -> Callable[[Coro], Coro]:
        """A decorator that registers another function as an external
        event listener. Basically this allows you to listen to multiple
        events from different places e.g. such as :func:`.on_ready`

        The functions being listened to must be a :ref:`coroutine <coroutine>`.

        Raises
        ------
        TypeError
            The function being listened to is not a coroutine.
        ValueError
            The ``name`` (event name) does not start with 'on_'

        Example
        -------

        .. code-block:: python3

            @client.listen()
            async def on_message(message):
                print('one')

            # in some other file...

            @client.listen('on_message')
            async def my_message(message):
                print('two')

            # listen to the first event only
            @client.listen('on_ready', once=True)
            async def on_ready():
                print('ready!')

        Would print one and two in an unspecified order.
        """

        def decorator(func: Coro) -> Coro:
            # Special case, where default should be overwritten
            if name == "on_application_command_error":
                return self.event(func)

            func._once = once
            self.add_listener(func, name)
            return func

        if asyncio.iscoroutinefunction(name):
            coro = name
            name = coro.__name__
            return decorator(coro)

        return decorator

    def event(self, coro: Coro) -> Coro:
        """A decorator that registers an event to listen to.

        You can find more info about the events on the :ref:`documentation below <discord-api-events>`.

        The events must be a :ref:`coroutine <coroutine>`, if not, :exc:`TypeError` is raised.

        .. note::

            This replaces any default handlers.
            Developers are encouraged to use :py:meth:`~discord.Client.listen` for adding additional handlers
            instead of :py:meth:`~discord.Client.event` unless default method replacement is intended.

        Raises
        ------
        TypeError
            The coroutine passed is not actually a coroutine.

        Example
        -------

        .. code-block:: python3

            @client.event
            async def on_ready():
                print('Ready!')
        """

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("event registered must be a coroutine function")

        setattr(self, coro.__name__, coro)
        _log.debug("%s has successfully been registered as an event", coro.__name__)
        return coro

    async def change_presence(
        self,
        *,
        activity: BaseActivity | None = None,
        status: Status | None = None,
    ):
        """|coro|

        Changes the client's presence.

        Parameters
        ----------
        activity: Optional[:class:`.BaseActivity`]
            The activity being done. ``None`` if no currently active activity is done.
        status: Optional[:class:`.Status`]
            Indicates what status to change to. If ``None``, then
            :attr:`.Status.online` is used.

        Raises
        ------
        :exc:`InvalidArgument`
            If the ``activity`` parameter is not the proper type.

        Example
        -------

        .. code-block:: python3

            game = discord.Game("with the API")
            await client.change_presence(status=discord.Status.idle, activity=game)

        .. versionchanged:: 2.0
            Removed the ``afk`` keyword-only parameter.
        """

        if status is None:
            status_str = "online"
            status = Status.online
        elif status is Status.offline:
            status_str = "invisible"
            status = Status.offline
        else:
            status_str = str(status)

        await self.ws.change_presence(activity=activity, status=status_str)

        for guild in self._connection.guilds:
            me = guild.me
            if me is None:
                continue

            me.activities = (activity,) if activity is not None else ()
            me.status = status

    # Guild stuff

    def fetch_guilds(
        self,
        *,
        limit: int | None = 100,
        before: SnowflakeTime = None,
        after: SnowflakeTime = None,
        with_counts: bool = True,
    ) -> GuildIterator:
        """Retrieves an :class:`.AsyncIterator` that enables receiving your guilds.

        .. note::

            Using this, you will only receive :attr:`.Guild.owner`, :attr:`.Guild.icon`,
            :attr:`.Guild.id`, and :attr:`.Guild.name` per :class:`.Guild`.

        .. note::

            This method is an API call. For general usage, consider :attr:`guilds` instead.

        Parameters
        ----------
        limit: Optional[:class:`int`]
            The number of guilds to retrieve.
            If ``None``, it retrieves every guild you have access to. Note, however,
            that this would make it a slow operation.
            Defaults to ``100``.
        before: Union[:class:`.abc.Snowflake`, :class:`datetime.datetime`]
            Retrieves guilds before this date or object.
            If a datetime is provided, it is recommended to use a UTC aware datetime.
            If the datetime is naive, it is assumed to be local time.
        after: Union[:class:`.abc.Snowflake`, :class:`datetime.datetime`]
            Retrieve guilds after this date or object.
            If a datetime is provided, it is recommended to use a UTC aware datetime.
            If the datetime is naive, it is assumed to be local time.
        with_counts: :class:`bool`
            Whether to include member count information in guilds. This fills the
            :attr:`.Guild.approximate_member_count` and :attr:`.Guild.approximate_presence_count`
            fields.
            Defaults to ``True``.

        Yields
        ------
        :class:`.Guild`
            The guild with the guild data parsed.

        Raises
        ------
        :exc:`HTTPException`
            Getting the guilds failed.

        Examples
        --------

        Usage ::

            async for guild in client.fetch_guilds(limit=150):
                print(guild.name)

        Flattening into a list ::

            guilds = await client.fetch_guilds(limit=150).flatten()
            # guilds is now a list of Guild...

        All parameters are optional.
        """
        return GuildIterator(
            self, limit=limit, before=before, after=after, with_counts=with_counts
        )

    async def fetch_template(self, code: Template | str) -> Template:
        """|coro|

        Gets a :class:`.Template` from a discord.new URL or code.

        Parameters
        ----------
        code: Union[:class:`.Template`, :class:`str`]
            The Discord Template Code or URL (must be a discord.new URL).

        Returns
        -------
        :class:`.Template`
            The template from the URL/code.

        Raises
        ------
        :exc:`NotFound`
            The template is invalid.
        :exc:`HTTPException`
            Getting the template failed.
        """
        code = utils.resolve_template(code)
        data = await self.http.get_template(code)
        return Template(data=data, state=self._connection)  # type: ignore

    async def fetch_guild(self, guild_id: int, /, *, with_counts=True) -> Guild:
        """|coro|

        Retrieves a :class:`.Guild` from an ID.

        .. note::

            Using this, you will **not** receive :attr:`.Guild.channels`, :attr:`.Guild.members`,
            :attr:`.Member.activity` and :attr:`.Member.voice` per :class:`.Member`.

        .. note::

            This method is an API call. For general usage, consider :meth:`get_guild` instead.

        Parameters
        ----------
        guild_id: :class:`int`
            The guild's ID to fetch from.

        with_counts: :class:`bool`
            Whether to include count information in the guild. This fills the
            :attr:`.Guild.approximate_member_count` and :attr:`.Guild.approximate_presence_count`
            fields.

            .. versionadded:: 2.0

        Returns
        -------
        :class:`.Guild`
            The guild from the ID.

        Raises
        ------
        :exc:`Forbidden`
            You do not have access to the guild.
        :exc:`HTTPException`
            Getting the guild failed.
        """
        data = await self.http.get_guild(guild_id, with_counts=with_counts)
        return Guild(data=data, state=self._connection)

    async def create_guild(
        self,
        *,
        name: str,
        icon: bytes = MISSING,
        code: str = MISSING,
    ) -> Guild:
        """|coro|

        Creates a :class:`.Guild`.

        Bot accounts in more than 10 guilds are not allowed to create guilds.

        Parameters
        ----------
        name: :class:`str`
            The name of the guild.
        icon: Optional[:class:`bytes`]
            The :term:`py:bytes-like object` representing the icon. See :meth:`.ClientUser.edit`
            for more details on what is expected.
        code: :class:`str`
            The code for a template to create the guild with.

            .. versionadded:: 1.4

        Returns
        -------
        :class:`.Guild`
            The guild created. This is not the same guild that is
            added to cache.

        Raises
        ------
        :exc:`HTTPException`
            Guild creation failed.
        :exc:`InvalidArgument`
            Invalid icon image format given. Must be PNG or JPG.
        """
        if icon is not MISSING:
            icon_base64 = utils._bytes_to_base64_data(icon)
        else:
            icon_base64 = None

        if code:
            data = await self.http.create_from_template(code, name, icon_base64)
        else:
            data = await self.http.create_guild(name, icon_base64)
        return Guild(data=data, state=self._connection)

    async def fetch_stage_instance(self, channel_id: int, /) -> StageInstance:
        """|coro|

        Gets a :class:`.StageInstance` for a stage channel id.

        .. versionadded:: 2.0

        Parameters
        ----------
        channel_id: :class:`int`
            The stage channel ID.

        Returns
        -------
        :class:`.StageInstance`
            The stage instance from the stage channel ID.

        Raises
        ------
        :exc:`NotFound`
            The stage instance or channel could not be found.
        :exc:`HTTPException`
            Getting the stage instance failed.
        """
        data = await self.http.get_stage_instance(channel_id)
        guild = self.get_guild(int(data["guild_id"]))
        return StageInstance(guild=guild, state=self._connection, data=data)  # type: ignore

    # Invite management

    async def fetch_invite(
        self,
        url: Invite | str,
        *,
        with_counts: bool = True,
        with_expiration: bool = True,
        event_id: int | None = None,
    ) -> Invite:
        """|coro|

        Gets an :class:`.Invite` from a discord.gg URL or ID.

        .. note::

            If the invite is for a guild you have not joined, the guild and channel
            attributes of the returned :class:`.Invite` will be :class:`.PartialInviteGuild` and
            :class:`.PartialInviteChannel` respectively.

        Parameters
        ----------
        url: Union[:class:`.Invite`, :class:`str`]
            The Discord invite ID or URL (must be a discord.gg URL).
        with_counts: :class:`bool`
            Whether to include count information in the invite. This fills the
            :attr:`.Invite.approximate_member_count` and :attr:`.Invite.approximate_presence_count`
            fields.
        with_expiration: :class:`bool`
            Whether to include the expiration date of the invite. This fills the
            :attr:`.Invite.expires_at` field.

            .. versionadded:: 2.0
        event_id: Optional[:class:`int`]
            The ID of the scheduled event to be associated with the event.

            See :meth:`Invite.set_scheduled_event` for more
            info on event invite linking.

            .. versionadded:: 2.0

        Returns
        -------
        :class:`.Invite`
            The invite from the URL/ID.

        Raises
        ------
        :exc:`NotFound`
            The invite has expired or is invalid.
        :exc:`HTTPException`
            Getting the invite failed.
        """

        invite_id = utils.resolve_invite(url)
        data = await self.http.get_invite(
            invite_id,
            with_counts=with_counts,
            with_expiration=with_expiration,
            guild_scheduled_event_id=event_id,
        )
        return Invite.from_incomplete(state=self._connection, data=data)

    async def delete_invite(self, invite: Invite | str) -> None:
        """|coro|

        Revokes an :class:`.Invite`, URL, or ID to an invite.

        You must have the :attr:`~.Permissions.manage_channels` permission in
        the associated guild to do this.

        Parameters
        ----------
        invite: Union[:class:`.Invite`, :class:`str`]
            The invite to revoke.

        Raises
        ------
        :exc:`Forbidden`
            You do not have permissions to revoke invites.
        :exc:`NotFound`
            The invite is invalid or expired.
        :exc:`HTTPException`
            Revoking the invite failed.
        """

        invite_id = utils.resolve_invite(invite)
        await self.http.delete_invite(invite_id)

    # Miscellaneous stuff

    async def fetch_widget(self, guild_id: int, /) -> Widget:
        """|coro|

        Gets a :class:`.Widget` from a guild ID.

        .. note::

            The guild must have the widget enabled to get this information.

        Parameters
        ----------
        guild_id: :class:`int`
            The ID of the guild.

        Returns
        -------
        :class:`.Widget`
            The guild's widget.

        Raises
        ------
        :exc:`Forbidden`
            The widget for this guild is disabled.
        :exc:`HTTPException`
            Retrieving the widget failed.
        """
        data = await self.http.get_widget(guild_id)

        return Widget(state=self._connection, data=data)

    async def application_info(self) -> AppInfo:
        """|coro|

        Retrieves the bot's application information.

        Returns
        -------
        :class:`.AppInfo`
            The bot's application information.

        Raises
        ------
        :exc:`HTTPException`
            Retrieving the information failed somehow.
        """
        data = await self.http.application_info()
        if "rpc_origins" not in data:
            data["rpc_origins"] = None
        return AppInfo(self._connection, data)

    async def fetch_user(self, user_id: int, /) -> User:
        """|coro|

        Retrieves a :class:`~discord.User` based on their ID.
        You do not have to share any guilds with the user to get this information,
        however many operations do require that you do.

        .. note::

            This method is an API call. If you have :attr:`discord.Intents.members` and member cache enabled,
            consider :meth:`get_user` instead.

        Parameters
        ----------
        user_id: :class:`int`
            The user's ID to fetch from.

        Returns
        -------
        :class:`~discord.User`
            The user you requested.

        Raises
        ------
        :exc:`NotFound`
            A user with this ID does not exist.
        :exc:`HTTPException`
            Fetching the user failed.
        """
        data = await self.http.get_user(user_id)
        return User(state=self._connection, data=data)

    async def fetch_channel(
        self, channel_id: int, /
    ) -> GuildChannel | PrivateChannel | Thread:
        """|coro|

        Retrieves a :class:`.abc.GuildChannel`, :class:`.abc.PrivateChannel`, or :class:`.Thread` with the specified ID.

        .. note::

            This method is an API call. For general usage, consider :meth:`get_channel` instead.

        .. versionadded:: 1.2

        Returns
        -------
        Union[:class:`.abc.GuildChannel`, :class:`.abc.PrivateChannel`, :class:`.Thread`]
            The channel from the ID.

        Raises
        ------
        :exc:`InvalidData`
            An unknown channel type was received from Discord.
        :exc:`HTTPException`
            Retrieving the channel failed.
        :exc:`NotFound`
            Invalid Channel ID.
        :exc:`Forbidden`
            You do not have permission to fetch this channel.
        """
        data = await self.http.get_channel(channel_id)

        factory, ch_type = _threaded_channel_factory(data["type"])
        if factory is None:
            raise InvalidData(
                "Unknown channel type {type} for channel ID {id}.".format_map(data)
            )

        if ch_type in (ChannelType.group, ChannelType.private):
            # the factory will be a DMChannel or GroupChannel here
            return factory(me=self.user, data=data, state=self._connection)
        # the factory can't be a DMChannel or GroupChannel here
        guild_id = int(data["guild_id"])  # type: ignore
        guild = self.get_guild(guild_id) or Object(id=guild_id)
        # GuildChannels expect a Guild, we may be passing an Object
        return factory(guild=guild, state=self._connection, data=data)

    async def fetch_webhook(self, webhook_id: int, /) -> Webhook:
        """|coro|

        Retrieves a :class:`.Webhook` with the specified ID.

        Returns
        -------
        :class:`.Webhook`
            The webhook you requested.

        Raises
        ------
        :exc:`HTTPException`
            Retrieving the webhook failed.
        :exc:`NotFound`
            Invalid webhook ID.
        :exc:`Forbidden`
            You do not have permission to fetch this webhook.
        """
        data = await self.http.get_webhook(webhook_id)
        return Webhook.from_state(data, state=self._connection)

    async def fetch_sticker(self, sticker_id: int, /) -> StandardSticker | GuildSticker:
        """|coro|

        Retrieves a :class:`.Sticker` with the specified ID.

        .. versionadded:: 2.0

        Returns
        -------
        Union[:class:`.StandardSticker`, :class:`.GuildSticker`]
            The sticker you requested.

        Raises
        ------
        :exc:`HTTPException`
            Retrieving the sticker failed.
        :exc:`NotFound`
            Invalid sticker ID.
        """
        data = await self.http.get_sticker(sticker_id)
        cls, _ = _sticker_factory(data["type"])  # type: ignore
        return cls(state=self._connection, data=data)  # type: ignore

    async def fetch_premium_sticker_packs(self) -> list[StickerPack]:
        """|coro|

        Retrieves all available premium sticker packs.

        .. versionadded:: 2.0

        Returns
        -------
        List[:class:`.StickerPack`]
            All available premium sticker packs.

        Raises
        ------
        :exc:`HTTPException`
            Retrieving the sticker packs failed.
        """
        data = await self.http.list_premium_sticker_packs()
        return [
            StickerPack(state=self._connection, data=pack)
            for pack in data["sticker_packs"]
        ]

    async def create_dm(self, user: Snowflake) -> DMChannel:
        """|coro|

        Creates a :class:`.DMChannel` with this user.

        This should be rarely called, as this is done transparently for most
        people.

        .. versionadded:: 2.0

        Parameters
        ----------
        user: :class:`~discord.abc.Snowflake`
            The user to create a DM with.

        Returns
        -------
        :class:`.DMChannel`
            The channel that was created.
        """
        state = self._connection
        found = state._get_private_channel_by_user(user.id)
        if found:
            return found

        data = await state.http.start_private_message(user.id)
        return state.add_dm_channel(data)

    def add_view(self, view: View, *, message_id: int | None = None) -> None:
        """Registers a :class:`~discord.ui.View` for persistent listening.

        This method should be used for when a view is comprised of components
        that last longer than the lifecycle of the program.

        .. versionadded:: 2.0

        Parameters
        ----------
        view: :class:`discord.ui.View`
            The view to register for dispatching.
        message_id: Optional[:class:`int`]
            The message ID that the view is attached to. This is currently used to
            refresh the view's state during message update events. If not given
            then message update events are not propagated for the view.

        Raises
        ------
        TypeError
            A view was not passed.
        ValueError
            The view is not persistent. A persistent view has no timeout
            and all their components have an explicitly provided ``custom_id``.
        """

        if not isinstance(view, View):
            raise TypeError(f"expected an instance of View not {view.__class__!r}")

        if not view.is_persistent():
            raise ValueError(
                "View is not persistent. Items need to have a custom_id set and View"
                " must have no timeout"
            )

        self._connection.store_view(view, message_id)

    @property
    def persistent_views(self) -> Sequence[View]:
        """A sequence of persistent views added to the client.

        .. versionadded:: 2.0
        """
        return self._connection.persistent_views

    async def fetch_role_connection_metadata_records(
        self,
    ) -> list[ApplicationRoleConnectionMetadata]:
        """|coro|

        Fetches the bot's role connection metadata records.

        .. versionadded:: 2.4

        Returns
        -------
        List[:class:`.ApplicationRoleConnectionMetadata`]
            The bot's role connection metadata records.
        """
        data = await self._connection.http.get_application_role_connection_metadata_records(
            self.application_id
        )
        return [ApplicationRoleConnectionMetadata.from_dict(r) for r in data]

    async def update_role_connection_metadata_records(
        self, *role_connection_metadata
    ) -> list[ApplicationRoleConnectionMetadata]:
        """|coro|

        Updates the bot's role connection metadata records.

        .. versionadded:: 2.4

        Parameters
        ----------
        *role_connection_metadata: :class:`ApplicationRoleConnectionMetadata`
            The new metadata records to send to Discord.

        Returns
        -------
        List[:class:`.ApplicationRoleConnectionMetadata`]
            The updated role connection metadata records.
        """
        payload = [r.to_dict() for r in role_connection_metadata]
        data = await self._connection.http.update_application_role_connection_metadata_records(
            self.application_id, payload
        )
        return [ApplicationRoleConnectionMetadata.from_dict(r) for r in data]

    async def fetch_skus(self) -> list[SKU]:
        """|coro|

        Fetches the bot's SKUs.

        .. versionadded:: 2.5

        Returns
        -------
        List[:class:`.SKU`]
            The bot's SKUs.
        """
        data = await self._connection.http.list_skus(self.application_id)
        return [SKU(state=self._connection, data=s) for s in data]

    def entitlements(
        self,
        user: Snowflake | None = None,
        skus: list[Snowflake] | None = None,
        before: SnowflakeTime | None = None,
        after: SnowflakeTime | None = None,
        limit: int | None = 100,
        guild: Snowflake | None = None,
        exclude_ended: bool = False,
    ) -> EntitlementIterator:
        """Returns an :class:`.AsyncIterator` that enables fetching the application's entitlements.

        .. versionadded:: 2.6

        Parameters
        ----------
        user: :class:`.abc.Snowflake` | None
            Limit the fetched entitlements to entitlements owned by this user.
        skus: list[:class:`.abc.Snowflake`] | None
            Limit the fetched entitlements to entitlements that are for these SKUs.
        before: :class:`.abc.Snowflake` | :class:`datetime.datetime` | None
            Retrieves guilds before this date or object.
            If a datetime is provided, it is recommended to use a UTC-aware datetime.
            If the datetime is naive, it is assumed to be local time.
        after: :class:`.abc.Snowflake` | :class:`datetime.datetime` | None
            Retrieve guilds after this date or object.
            If a datetime is provided, it is recommended to use a UTC-aware datetime.
            If the datetime is naive, it is assumed to be local time.
        limit: Optional[:class:`int`]
            The number of entitlements to retrieve.
            If ``None``, retrieves every entitlement, which may be slow.
            Defaults to ``100``.
        guild: :class:`.abc.Snowflake` | None
            Limit the fetched entitlements to entitlements owned by this guild.
        exclude_ended: :class:`bool`
            Whether to limit the fetched entitlements to those that have not ended.
            Defaults to ``False``.

        Yields
        ------
        :class:`.Entitlement`
            The application's entitlements.

        Raises
        ------
        :exc:`HTTPException`
            Retrieving the entitlements failed.

        Examples
        --------

        Usage ::

            async for entitlement in client.entitlements():
                print(entitlement.user_id)

        Flattening into a list ::

            entitlements = await user.entitlements().flatten()

        All parameters are optional.
        """
        return EntitlementIterator(
            self._connection,
            user_id=user.id if user else None,
            sku_ids=[sku.id for sku in skus] if skus else None,
            before=before,
            after=after,
            limit=limit,
            guild_id=guild.id if guild else None,
            exclude_ended=exclude_ended,
        )

    @property
    def store_url(self) -> str:
        """:class:`str`: The URL that leads to the application's store page for monetization.

        .. versionadded:: 2.6
        """
        return f"https://discord.com/application-directory/{self.application_id}/store"

    async def fetch_emojis(self) -> list[AppEmoji]:
        r"""|coro|

        Retrieves all custom :class:`AppEmoji`\s from the application.

        Raises
        ---------
        HTTPException
            An error occurred fetching the emojis.

        Returns
        --------
        List[:class:`AppEmoji`]
            The retrieved emojis.
        """
        data = await self._connection.http.get_all_application_emojis(
            self.application_id
        )
        return [
            self._connection.maybe_store_app_emoji(self.application_id, d)
            for d in data["items"]
        ]

    async def fetch_emoji(self, emoji_id: int, /) -> AppEmoji:
        """|coro|

        Retrieves a custom :class:`AppEmoji` from the application.

        Parameters
        ----------
        emoji_id: :class:`int`
            The emoji's ID.

        Returns
        -------
        :class:`AppEmoji`
            The retrieved emoji.

        Raises
        ------
        NotFound
            The emoji requested could not be found.
        HTTPException
            An error occurred fetching the emoji.
        """
        data = await self._connection.http.get_application_emoji(
            self.application_id, emoji_id
        )
        return self._connection.maybe_store_app_emoji(self.application_id, data)

    async def create_emoji(
        self,
        *,
        name: str,
        image: bytes,
    ) -> AppEmoji:
        r"""|coro|

        Creates a custom :class:`AppEmoji` for the application.

        There is currently a limit of 2000 emojis per application.

        Parameters
        -----------
        name: :class:`str`
            The emoji name. Must be at least 2 characters.
        image: :class:`bytes`
            The :term:`py:bytes-like object` representing the image data to use.
            Only JPG, PNG and GIF images are supported.

        Raises
        -------
        HTTPException
            An error occurred creating an emoji.

        Returns
        --------
        :class:`AppEmoji`
            The created emoji.
        """

        img = utils._bytes_to_base64_data(image)
        data = await self._connection.http.create_application_emoji(
            self.application_id, name, img
        )
        return self._connection.maybe_store_app_emoji(self.application_id, data)

    async def delete_emoji(self, emoji: Snowflake) -> None:
        """|coro|

        Deletes the custom :class:`AppEmoji` from the application.

        Parameters
        ----------
        emoji: :class:`abc.Snowflake`
            The emoji you are deleting.

        Raises
        ------
        HTTPException
            An error occurred deleting the emoji.
        """

        await self._connection.http.delete_application_emoji(
            self.application_id, emoji.id
        )
        if self._connection.cache_app_emojis and self._connection.get_emoji(emoji.id):
            self._connection.remove_emoji(emoji)
