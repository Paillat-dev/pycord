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
import sys
import weakref
from typing import TYPE_CHECKING, Any, Coroutine, Iterable, Sequence, TypeVar
from urllib.parse import quote as _uriquote

import aiohttp

from . import __version__, utils
from .errors import (
    DiscordServerError,
    Forbidden,
    GatewayNotFound,
    HTTPException,
    InvalidArgument,
    LoginFailure,
    NotFound,
)
from .file import VoiceMessage
from .gateway import DiscordClientWebSocketResponse
from .utils import MISSING, warn_deprecated

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from types import TracebackType

    from .enums import AuditLogAction, InteractionResponseType
    from .file import File
    from .types import (
        appinfo,
        application_role_connection,
        audit_log,
        automod,
        channel,
        components,
        embed,
        emoji,
        guild,
        integration,
        interactions,
        invite,
        member,
        message,
        monetization,
        onboarding,
        poll,
        role,
        scheduled_events,
        sticker,
        template,
        threads,
        user,
        webhook,
        welcome_screen,
        widget,
    )
    from .types.snowflake import Snowflake, SnowflakeList

    T = TypeVar("T")
    BE = TypeVar("BE", bound=BaseException)
    MU = TypeVar("MU", bound="MaybeUnlock")
    Response = Coroutine[Any, Any, T]

API_VERSION: int = 10


async def json_or_text(response: aiohttp.ClientResponse) -> dict[str, Any] | str:
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            return utils._from_json(text)
    except KeyError:
        # Thanks Cloudflare
        pass

    return text


class Route:
    API_BASE_URL: str = "https://discord.com/api/v{API_VERSION}"

    def __init__(self, method: str, path: str, **parameters: Any) -> None:
        self.path: str = path
        self.method: str = method
        url = self.base + self.path
        if parameters:
            url = url.format_map(
                {
                    k: _uriquote(v) if isinstance(v, str) else v
                    for k, v in parameters.items()
                }
            )
        self.url: str = url

        # major parameters:
        self.channel_id: Snowflake | None = parameters.get("channel_id")
        self.guild_id: Snowflake | None = parameters.get("guild_id")
        self.webhook_id: Snowflake | None = parameters.get("webhook_id")
        self.webhook_token: str | None = parameters.get("webhook_token")

    @property
    def base(self) -> str:
        return self.API_BASE_URL.format(API_VERSION=API_VERSION)

    @property
    def bucket(self) -> str:
        # the bucket is just method + path w/ major parameters
        return f"{self.channel_id}:{self.guild_id}:{self.path}"


class MaybeUnlock:
    def __init__(self, lock: asyncio.Lock) -> None:
        self.lock: asyncio.Lock = lock
        self._unlock: bool = True

    def __enter__(self: MU) -> MU:
        return self

    def defer(self) -> None:
        self._unlock = False

    def __exit__(
        self,
        exc_type: type[BE] | None,
        exc: BE | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._unlock:
            self.lock.release()


# For some reason, the Discord voice websocket expects this header to be
# completely lowercase while aiohttp respects spec and does it as case-insensitive
aiohttp.hdrs.WEBSOCKET = "websocket"  # type: ignore


class HTTPClient:
    """Represents an HTTP client sending HTTP requests to the Discord API."""

    def __init__(
        self,
        connector: aiohttp.BaseConnector | None = None,
        *,
        proxy: str | None = None,
        proxy_auth: aiohttp.BasicAuth | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
        unsync_clock: bool = True,
    ) -> None:
        self.loop: asyncio.AbstractEventLoop = (
            asyncio.get_event_loop() if loop is None else loop
        )
        self.connector = connector
        self.__session: aiohttp.ClientSession = MISSING  # filled in static_login
        self._locks: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
        self._global_over: asyncio.Event = asyncio.Event()
        self._global_over.set()
        self.token: str | None = None
        self.bot_token: bool = False
        self.proxy: str | None = proxy
        self.proxy_auth: aiohttp.BasicAuth | None = proxy_auth
        self.use_clock: bool = not unsync_clock

        user_agent = (
            "DiscordBot (https://pycord.dev, {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"
        )
        self.user_agent: str = user_agent.format(
            __version__, sys.version_info, aiohttp.__version__
        )

    def recreate(self) -> None:
        if self.__session.closed:
            self.__session = aiohttp.ClientSession(
                connector=self.connector,
                ws_response_class=DiscordClientWebSocketResponse,
            )

    async def ws_connect(self, url: str, *, compress: int = 0) -> Any:
        kwargs = {
            "proxy_auth": self.proxy_auth,
            "proxy": self.proxy,
            "max_msg_size": 0,
            "timeout": 30.0,
            "autoclose": False,
            "headers": {
                "User-Agent": self.user_agent,
            },
            "compress": compress,
        }

        return await self.__session.ws_connect(url, **kwargs)

    async def request(
        self,
        route: Route,
        *,
        files: Sequence[File] | None = None,
        form: Iterable[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> Any:
        bucket = route.bucket
        method = route.method
        url = route.url

        lock = self._locks.get(bucket)
        if lock is None:
            lock = asyncio.Lock()
            if bucket is not None:
                self._locks[bucket] = lock

        # header creation
        headers: dict[str, str] = {
            "User-Agent": self.user_agent,
        }

        if self.token is not None:
            headers["Authorization"] = f"Bot {self.token}"
        # some checking if it's a JSON request
        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = utils._to_json(kwargs.pop("json"))

        try:
            reason = kwargs.pop("reason")
        except KeyError:
            pass
        else:
            if reason:
                headers["X-Audit-Log-Reason"] = _uriquote(reason, safe="/ ")

        if locale := kwargs.pop("locale", None):
            headers["X-Discord-Locale"] = locale

        kwargs["headers"] = headers
        # Proxy support
        if self.proxy is not None:
            kwargs["proxy"] = self.proxy
        if self.proxy_auth is not None:
            kwargs["proxy_auth"] = self.proxy_auth

        if not self._global_over.is_set():
            # wait until the global lock is complete
            await self._global_over.wait()

        response: aiohttp.ClientResponse | None = None
        data: dict[str, Any] | str | None = None
        await lock.acquire()
        with MaybeUnlock(lock) as maybe_lock:
            for tries in range(5):
                if files:
                    for f in files:
                        f.reset(seek=tries)

                if form:
                    form_data = aiohttp.FormData(quote_fields=False)
                    for params in form:
                        form_data.add_field(**params)
                    kwargs["data"] = form_data

                try:
                    async with self.__session.request(
                        method, url, **kwargs
                    ) as response:
                        _log.debug(
                            "%s %s with %s has returned %s",
                            method,
                            url,
                            kwargs.get("data"),
                            response.status,
                        )

                        # even errors have text involved in them so this is safe to call
                        data = await json_or_text(response)

                        # check if we have rate limit header information
                        remaining = response.headers.get("X-Ratelimit-Remaining")
                        if remaining == "0" and response.status != 429:
                            # we've depleted our current bucket
                            delta = utils._parse_ratelimit_header(
                                response, use_clock=self.use_clock
                            )
                            _log.debug(
                                (
                                    "A rate limit bucket has been exhausted (bucket:"
                                    " %s, retry: %s)."
                                ),
                                bucket,
                                delta,
                            )
                            maybe_lock.defer()
                            self.loop.call_later(delta, lock.release)

                        # the request was successful so just return the text/json
                        if 300 > response.status >= 200:
                            _log.debug("%s %s has received %s", method, url, data)
                            return data

                        # we are being rate limited
                        if response.status == 429:
                            if not response.headers.get("Via") or isinstance(data, str):
                                # Banned by Cloudflare more than likely.
                                raise HTTPException(response, data)

                            fmt = (
                                "We are being rate limited. Retrying in %.2f seconds."
                                ' Handled under the bucket "%s"'
                            )

                            # sleep a bit
                            retry_after: float = data["retry_after"]
                            _log.warning(fmt, retry_after, bucket)

                            # check if it's a global rate limit
                            is_global = data.get("global", False)
                            if is_global:
                                _log.warning(
                                    (
                                        "Global rate limit has been hit. Retrying in"
                                        " %.2f seconds."
                                    ),
                                    retry_after,
                                )
                                self._global_over.clear()

                            await asyncio.sleep(retry_after)
                            _log.debug("Done sleeping for the rate limit. Retrying...")

                            # release the global lock now that the
                            # global rate limit has passed
                            if is_global:
                                self._global_over.set()
                                _log.debug("Global rate limit is now over.")

                            continue

                        # we've received a 500, 502, 503, or 504, unconditional retry
                        if response.status in {500, 502, 503, 504}:
                            await asyncio.sleep(1 + tries * 2)
                            continue

                        # the usual error cases
                        if response.status == 403:
                            raise Forbidden(response, data)
                        elif response.status == 404:
                            raise NotFound(response, data)
                        elif response.status >= 500:
                            raise DiscordServerError(response, data)
                        else:
                            raise HTTPException(response, data)

                # This is handling exceptions from the request
                except OSError as e:
                    # Connection reset by peer
                    if tries < 4 and e.errno in (54, 10054):
                        await asyncio.sleep(1 + tries * 2)
                        continue
                    raise

            if response is not None:
                # We've run out of retries, raise.
                if response.status >= 500:
                    raise DiscordServerError(response, data)

                raise HTTPException(response, data)

            raise RuntimeError("Unreachable code in HTTP handling")

    async def get_from_cdn(self, url: str) -> bytes:
        async with self.__session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()
            elif resp.status == 404:
                raise NotFound(resp, "asset not found")
            elif resp.status == 403:
                raise Forbidden(resp, "cannot retrieve asset")
            else:
                raise HTTPException(resp, "failed to get asset")

    # state management

    async def close(self) -> None:
        if self.__session:
            await self.__session.close()

    # login management

    async def static_login(self, token: str) -> user.User:
        # Necessary to get aiohttp to stop complaining about session creation
        self.__session = aiohttp.ClientSession(
            connector=self.connector, ws_response_class=DiscordClientWebSocketResponse
        )
        old_token = self.token
        self.token = token

        try:
            data = await self.request(Route("GET", "/users/@me"))
        except HTTPException as exc:
            self.token = old_token
            if exc.status == 401:
                raise LoginFailure("Improper token has been passed.") from exc
            raise

        return data

    def logout(self) -> Response[None]:
        return self.request(Route("POST", "/auth/logout"))

    # Group functionality

    def start_group(
        self, user_id: Snowflake, recipients: list[int]
    ) -> Response[channel.GroupDMChannel]:
        payload = {
            "recipients": recipients,
        }

        return self.request(
            Route("POST", "/users/{user_id}/channels", user_id=user_id), json=payload
        )

    def leave_group(self, channel_id) -> Response[None]:
        return self.request(
            Route("DELETE", "/channels/{channel_id}", channel_id=channel_id)
        )

    # Message management

    def start_private_message(self, user_id: Snowflake) -> Response[channel.DMChannel]:
        payload = {
            "recipient_id": user_id,
        }

        return self.request(Route("POST", "/users/@me/channels"), json=payload)

    def send_message(
        self,
        channel_id: Snowflake,
        content: str | None,
        *,
        tts: bool = False,
        embed: embed.Embed | None = None,
        embeds: list[embed.Embed] | None = None,
        nonce: int | str | None = None,
        enforce_nonce: bool | None = None,
        allowed_mentions: message.AllowedMentions | None = None,
        message_reference: message.MessageReference | None = None,
        stickers: list[sticker.StickerItem] | None = None,
        components: list[components.Component] | None = None,
        flags: int | None = None,
        poll: poll.Poll | None = None,
    ) -> Response[message.Message]:
        r = Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id)
        payload = {}

        if content:
            payload["content"] = content

        if tts:
            payload["tts"] = True

        if embed:
            payload["embeds"] = [embed]

        if embeds:
            payload["embeds"] = embeds

        if nonce:
            payload["nonce"] = nonce

        if enforce_nonce:
            payload["enforce_nonce"] = enforce_nonce

        if allowed_mentions:
            payload["allowed_mentions"] = allowed_mentions

        if message_reference:
            payload["message_reference"] = message_reference

        if components:
            payload["components"] = components

        if stickers:
            payload["sticker_ids"] = stickers

        if flags:
            payload["flags"] = flags

        if poll:
            payload["poll"] = poll

        return self.request(r, json=payload)

    def send_typing(self, channel_id: Snowflake) -> Response[None]:
        return self.request(
            Route("POST", "/channels/{channel_id}/typing", channel_id=channel_id)
        )

    def send_multipart_helper(
        self,
        route: Route,
        *,
        files: Sequence[File],
        content: str | None = None,
        tts: bool = False,
        embed: embed.Embed | None = None,
        embeds: Iterable[embed.Embed | None] | None = None,
        nonce: int | str | None = None,
        enforce_nonce: bool | None = None,
        allowed_mentions: message.AllowedMentions | None = None,
        message_reference: message.MessageReference | None = None,
        stickers: list[sticker.StickerItem] | None = None,
        components: list[components.Component] | None = None,
        flags: int | None = None,
        poll: poll.Poll | None = None,
    ) -> Response[message.Message]:
        form = []

        payload: dict[str, Any] = {"tts": tts}
        if content:
            payload["content"] = content
        if embed:
            payload["embeds"] = [embed]
        if embeds:
            payload["embeds"] = embeds
        if nonce:
            payload["nonce"] = nonce
        if enforce_nonce:
            payload["enforce_nonce"] = enforce_nonce
        if allowed_mentions:
            payload["allowed_mentions"] = allowed_mentions
        if message_reference:
            payload["message_reference"] = message_reference
        if components:
            payload["components"] = components
        if stickers:
            payload["sticker_ids"] = stickers
        if flags:
            payload["flags"] = flags
        if poll:
            payload["poll"] = poll

        attachments = []
        form.append({"name": "payload_json"})
        for index, file in enumerate(files):
            attachment_info = {
                "id": index,
                "filename": file.filename,
                "description": file.description,
            }
            if isinstance(file, VoiceMessage):
                attachment_info.update(
                    waveform=file.waveform,
                    duration_secs=file.duration_secs,
                )
            attachments.append(attachment_info)
            form.append(
                {
                    "name": f"files[{index}]",
                    "value": file.fp,
                    "filename": file.filename,
                    "content_type": "application/octet-stream",
                }
            )
        payload["attachments"] = attachments
        form[0]["value"] = utils._to_json(payload)
        return self.request(route, form=form, files=files)

    def send_files(
        self,
        channel_id: Snowflake,
        *,
        files: Sequence[File],
        content: str | None = None,
        tts: bool = False,
        embed: embed.Embed | None = None,
        embeds: list[embed.Embed] | None = None,
        nonce: int | str | None = None,
        enforce_nonce: bool | None = None,
        allowed_mentions: message.AllowedMentions | None = None,
        message_reference: message.MessageReference | None = None,
        stickers: list[sticker.StickerItem] | None = None,
        components: list[components.Component] | None = None,
        flags: int | None = None,
        poll: poll.Poll | None = None,
    ) -> Response[message.Message]:
        r = Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id)
        return self.send_multipart_helper(
            r,
            files=files,
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            nonce=nonce,
            enforce_nonce=enforce_nonce,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            stickers=stickers,
            components=components,
            flags=flags,
            poll=poll,
        )

    def edit_multipart_helper(
        self,
        route: Route,
        files: Sequence[File],
        **payload,
    ) -> Response[message.Message]:
        form = []

        attachments = []
        form.append({"name": "payload_json"})
        for index, file in enumerate(files):
            attachment_info = {
                "id": index,
                "filename": file.filename,
                "description": file.description,
            }
            if isinstance(file, VoiceMessage):
                attachment_info.update(
                    waveform=file.waveform,
                    duration_secs=file.duration_secs,
                )
            attachments.append(attachment_info)
            form.append(
                {
                    "name": f"files[{index}]",
                    "value": file.fp,
                    "filename": file.filename,
                    "content_type": "application/octet-stream",
                }
            )
        if "attachments" not in payload:
            payload["attachments"] = attachments
        else:
            payload["attachments"].extend(attachments)
        form[0]["value"] = utils._to_json(payload)

        return self.request(route, form=form, files=files)

    def edit_files(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        files: Sequence[File],
        **fields,
    ) -> Response[message.Message]:
        r = Route(
            "PATCH",
            f"/channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )
        payload: dict[str, Any] = {}
        if "attachments" in fields:
            payload["attachments"] = fields["attachments"]
        if "flags" in fields:
            payload["flags"] = fields["flags"]
        if "content" in fields:
            payload["content"] = fields["content"]
        if "embeds" in fields:
            payload["embeds"] = fields["embeds"]
        if "allowed_mentions" in fields:
            payload["allowed_mentions"] = fields["allowed_mentions"]
        if "components" in fields:
            payload["components"] = fields["components"]
        return self.edit_multipart_helper(
            r,
            files=files,
            **payload,
        )

    def delete_message(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )
        return self.request(r, reason=reason)

    def delete_messages(
        self,
        channel_id: Snowflake,
        message_ids: SnowflakeList,
        *,
        reason: str | None = None,
    ) -> Response[None]:
        r = Route(
            "POST", "/channels/{channel_id}/messages/bulk-delete", channel_id=channel_id
        )
        payload = {
            "messages": message_ids,
        }

        return self.request(r, json=payload, reason=reason)

    def edit_message(
        self, channel_id: Snowflake, message_id: Snowflake, **fields: Any
    ) -> Response[message.Message]:
        r = Route(
            "PATCH",
            "/channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )
        return self.request(r, json=fields)

    def add_reaction(
        self, channel_id: Snowflake, message_id: Snowflake, emoji: str
    ) -> Response[None]:
        r = Route(
            "PUT",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
        )
        return self.request(r)

    def remove_reaction(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        emoji: str,
        member_id: Snowflake,
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{member_id}",
            channel_id=channel_id,
            message_id=message_id,
            member_id=member_id,
            emoji=emoji,
        )
        return self.request(r)

    def remove_own_reaction(
        self, channel_id: Snowflake, message_id: Snowflake, emoji: str
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
        )
        return self.request(r)

    def get_reaction_users(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        emoji: str,
        limit: int,
        after: Snowflake | None = None,
        type: int | None = None,
    ) -> Response[list[user.User]]:
        r = Route(
            "GET",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
        )

        params: dict[str, Any] = {
            "limit": limit,
        }
        if after:
            params["after"] = after
        if type:
            params["type"] = type
        return self.request(r, params=params)

    def clear_reactions(
        self, channel_id: Snowflake, message_id: Snowflake
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions",
            channel_id=channel_id,
            message_id=message_id,
        )

        return self.request(r)

    def clear_single_reaction(
        self, channel_id: Snowflake, message_id: Snowflake, emoji: str
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
        )
        return self.request(r)

    def get_message(
        self, channel_id: Snowflake, message_id: Snowflake
    ) -> Response[message.Message]:
        r = Route(
            "GET",
            "/channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )
        return self.request(r)

    def get_channel(self, channel_id: Snowflake) -> Response[channel.Channel]:
        r = Route("GET", "/channels/{channel_id}", channel_id=channel_id)
        return self.request(r)

    def logs_from(
        self,
        channel_id: Snowflake,
        limit: int,
        before: Snowflake | None = None,
        after: Snowflake | None = None,
        around: Snowflake | None = None,
    ) -> Response[list[message.Message]]:
        params: dict[str, Any] = {
            "limit": limit,
        }

        if before is not None:
            params["before"] = before
        if after is not None:
            params["after"] = after
        if around is not None:
            params["around"] = around

        return self.request(
            Route("GET", "/channels/{channel_id}/messages", channel_id=channel_id),
            params=params,
        )

    def publish_message(
        self, channel_id: Snowflake, message_id: Snowflake
    ) -> Response[message.Message]:
        return self.request(
            Route(
                "POST",
                "/channels/{channel_id}/messages/{message_id}/crosspost",
                channel_id=channel_id,
                message_id=message_id,
            )
        )

    def pin_message(
        self, channel_id: Snowflake, message_id: Snowflake, reason: str | None = None
    ) -> Response[None]:
        r = Route(
            "PUT",
            "/channels/{channel_id}/pins/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )
        return self.request(r, reason=reason)

    def unpin_message(
        self, channel_id: Snowflake, message_id: Snowflake, reason: str | None = None
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/channels/{channel_id}/pins/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )
        return self.request(r, reason=reason)

    def pins_from(self, channel_id: Snowflake) -> Response[list[message.Message]]:
        return self.request(
            Route("GET", "/channels/{channel_id}/pins", channel_id=channel_id)
        )

    # Member management

    def kick(
        self, user_id: Snowflake, guild_id: Snowflake, reason: str | None = None
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/guilds/{guild_id}/members/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
        return self.request(r, reason=reason)

    def ban(
        self,
        user_id: Snowflake,
        guild_id: Snowflake,
        delete_message_seconds: int = None,
        reason: str | None = None,
    ) -> Response[None]:
        r = Route(
            "PUT",
            "/guilds/{guild_id}/bans/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
        params = {}

        if delete_message_seconds:
            params["delete_message_seconds"] = delete_message_seconds

        return self.request(r, params=params, reason=reason)

    def bulk_ban(
        self,
        user_ids: list[Snowflake],
        guild_id: Snowflake,
        delete_message_seconds: int = None,
        reason: str | None = None,
    ) -> Response[guild.GuildBulkBan]:
        r = Route(
            "POST",
            "/guilds/{guild_id}/bulk-ban",
            guild_id=guild_id,
        )
        payload = {
            "user_ids": user_ids,
        }
        if delete_message_seconds:
            payload["delete_message_seconds"] = delete_message_seconds

        return self.request(r, json=payload, reason=reason)

    def unban(
        self, user_id: Snowflake, guild_id: Snowflake, *, reason: str | None = None
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/guilds/{guild_id}/bans/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
        return self.request(r, reason=reason)

    def guild_voice_state(
        self,
        user_id: Snowflake,
        guild_id: Snowflake,
        *,
        mute: bool | None = None,
        deafen: bool | None = None,
        reason: str | None = None,
    ) -> Response[member.Member]:
        r = Route(
            "PATCH",
            "/guilds/{guild_id}/members/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
        payload = {}
        if mute is not None:
            payload["mute"] = mute

        if deafen is not None:
            payload["deaf"] = deafen

        return self.request(r, json=payload, reason=reason)

    def edit_profile(self, payload: dict[str, Any]) -> Response[user.User]:
        return self.request(Route("PATCH", "/users/@me"), json=payload)

    def change_my_nickname(
        self,
        guild_id: Snowflake,
        nickname: str,
        *,
        reason: str | None = None,
    ) -> Response[member.Nickname]:
        r = Route("PATCH", "/guilds/{guild_id}/members/@me", guild_id=guild_id)
        payload = {
            "nick": nickname,
        }
        return self.request(r, json=payload, reason=reason)

    def change_nickname(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        nickname: str,
        *,
        reason: str | None = None,
    ) -> Response[member.Member]:
        r = Route(
            "PATCH",
            "/guilds/{guild_id}/members/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
        payload = {
            "nick": nickname,
        }
        return self.request(r, json=payload, reason=reason)

    def edit_my_voice_state(
        self, guild_id: Snowflake, payload: dict[str, Any]
    ) -> Response[None]:
        r = Route("PATCH", "/guilds/{guild_id}/voice-states/@me", guild_id=guild_id)
        return self.request(r, json=payload)

    def edit_voice_state(
        self, guild_id: Snowflake, user_id: Snowflake, payload: dict[str, Any]
    ) -> Response[None]:
        r = Route(
            "PATCH",
            "/guilds/{guild_id}/voice-states/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
        return self.request(r, json=payload)

    def edit_member(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        reason: str | None = None,
        **fields: Any,
    ) -> Response[member.MemberWithUser]:
        r = Route(
            "PATCH",
            "/guilds/{guild_id}/members/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
        return self.request(r, json=fields, reason=reason)

    # Channel management

    def edit_channel(
        self,
        channel_id: Snowflake,
        *,
        reason: str | None = None,
        **options: Any,
    ) -> Response[channel.Channel]:
        r = Route("PATCH", "/channels/{channel_id}", channel_id=channel_id)
        valid_keys = (
            "name",
            "parent_id",
            "topic",
            "bitrate",
            "nsfw",
            "user_limit",
            "position",
            "permission_overwrites",
            "rate_limit_per_user",
            "type",
            "rtc_region",
            "video_quality_mode",
            "archived",
            "auto_archive_duration",
            "locked",
            "invitable",
            "default_auto_archive_duration",
            "flags",
            "default_thread_rate_limit_per_user",
            "default_reaction_emoji",
            "available_tags",
            "applied_tags",
            "default_sort_order",
        )
        payload = {k: v for k, v in options.items() if k in valid_keys}
        return self.request(r, reason=reason, json=payload)

    def bulk_channel_update(
        self,
        guild_id: Snowflake,
        data: list[guild.ChannelPositionUpdate],
        *,
        reason: str | None = None,
    ) -> Response[None]:
        r = Route("PATCH", "/guilds/{guild_id}/channels", guild_id=guild_id)
        return self.request(r, json=data, reason=reason)

    def create_channel(
        self,
        guild_id: Snowflake,
        channel_type: channel.ChannelType,
        *,
        reason: str | None = None,
        **options: Any,
    ) -> Response[channel.GuildChannel]:
        payload = {
            "type": channel_type,
        }

        valid_keys = (
            "name",
            "parent_id",
            "topic",
            "bitrate",
            "nsfw",
            "user_limit",
            "position",
            "permission_overwrites",
            "rate_limit_per_user",
            "rtc_region",
            "video_quality_mode",
            "auto_archive_duration",
            "default_reaction_emoji",
        )
        payload.update(
            {k: v for k, v in options.items() if k in valid_keys and v is not None}
        )

        return self.request(
            Route("POST", "/guilds/{guild_id}/channels", guild_id=guild_id),
            json=payload,
            reason=reason,
        )

    def delete_channel(
        self,
        channel_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> Response[None]:
        return self.request(
            Route("DELETE", "/channels/{channel_id}", channel_id=channel_id),
            reason=reason,
        )

    # Thread management

    def start_thread_with_message(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        *,
        name: str,
        auto_archive_duration: threads.ThreadArchiveDuration,
        rate_limit_per_user: int,
        reason: str | None = None,
    ) -> Response[threads.Thread]:
        payload = {
            "name": name,
            "auto_archive_duration": auto_archive_duration,
            "rate_limit_per_user": rate_limit_per_user,
        }

        route = Route(
            "POST",
            "/channels/{channel_id}/messages/{message_id}/threads",
            channel_id=channel_id,
            message_id=message_id,
        )
        return self.request(route, json=payload, reason=reason)

    def start_thread_without_message(
        self,
        channel_id: Snowflake,
        *,
        name: str,
        auto_archive_duration: threads.ThreadArchiveDuration,
        type: threads.ThreadType,
        rate_limit_per_user: int,
        invitable: bool,
        reason: str | None = None,
    ) -> Response[threads.Thread]:
        payload = {
            "name": name,
            "auto_archive_duration": auto_archive_duration,
            "type": type,
            "rate_limit_per_user": rate_limit_per_user,
            "invitable": invitable,
        }

        route = Route("POST", "/channels/{channel_id}/threads", channel_id=channel_id)
        return self.request(route, json=payload, reason=reason)

    def start_forum_thread(
        self,
        channel_id: Snowflake,
        content: str | None,
        *,
        name: str,
        auto_archive_duration: threads.ThreadArchiveDuration,
        rate_limit_per_user: int,
        invitable: bool = True,
        applied_tags: SnowflakeList | None = None,
        reason: str | None = None,
        files: Sequence[File] | None = None,
        embed: embed.Embed | None = None,
        embeds: list[embed.Embed] | None = None,
        nonce: int | str | None = None,
        allowed_mentions: message.AllowedMentions | None = None,
        stickers: list[sticker.StickerItem] | None = None,
        components: list[components.Component] | None = None,
        flags: int | None = None,
    ) -> Response[threads.Thread]:
        payload: dict[str, Any] = {
            "name": name,
            "auto_archive_duration": auto_archive_duration,
            "invitable": invitable,
        }

        if applied_tags:
            payload["applied_tags"] = applied_tags

        if rate_limit_per_user:
            payload["rate_limit_per_user"] = rate_limit_per_user

        message = {}

        if content:
            message["content"] = content

        if embed:
            message["embeds"] = [embed]

        if embeds:
            message["embeds"] = embeds

        if nonce:
            message["nonce"] = nonce

        if allowed_mentions:
            message["allowed_mentions"] = allowed_mentions

        if components:
            message["components"] = components

        if stickers:
            message["sticker_ids"] = stickers

        if flags:
            message["flags"] = flags

        if message != {}:
            payload["message"] = message

        route = Route(
            "POST",
            "/channels/{channel_id}/threads",
            channel_id=channel_id,
        )

        if files:
            form = [{"name": "payload_json"}]

            attachments = []
            for index, file in enumerate(files):
                attachments.append(
                    {
                        "id": index,
                        "filename": file.filename,
                        "description": file.description,
                    }
                )
                form.append(
                    {
                        "name": f"files[{index}]",
                        "value": file.fp,
                        "filename": file.filename,
                        "content_type": "application/octet-stream",
                    }
                )

            payload["attachments"] = attachments
            form[0]["value"] = utils._to_json(payload)
            return self.request(route, form=form, reason=reason)
        return self.request(route, json=payload, reason=reason)

    def join_thread(self, channel_id: Snowflake) -> Response[None]:
        return self.request(
            Route(
                "PUT",
                "/channels/{channel_id}/thread-members/@me",
                channel_id=channel_id,
            )
        )

    def add_user_to_thread(
        self, channel_id: Snowflake, user_id: Snowflake
    ) -> Response[None]:
        return self.request(
            Route(
                "PUT",
                "/channels/{channel_id}/thread-members/{user_id}",
                channel_id=channel_id,
                user_id=user_id,
            )
        )

    def leave_thread(self, channel_id: Snowflake) -> Response[None]:
        return self.request(
            Route(
                "DELETE",
                "/channels/{channel_id}/thread-members/@me",
                channel_id=channel_id,
            )
        )

    def remove_user_from_thread(
        self, channel_id: Snowflake, user_id: Snowflake
    ) -> Response[None]:
        route = Route(
            "DELETE",
            "/channels/{channel_id}/thread-members/{user_id}",
            channel_id=channel_id,
            user_id=user_id,
        )
        return self.request(route)

    def get_public_archived_threads(
        self, channel_id: Snowflake, before: Snowflake | None = None, limit: int = 50
    ) -> Response[threads.ThreadPaginationPayload]:
        route = Route(
            "GET",
            "/channels/{channel_id}/threads/archived/public",
            channel_id=channel_id,
        )

        params = {}
        if before:
            params["before"] = before
        params["limit"] = limit
        return self.request(route, params=params)

    def get_private_archived_threads(
        self, channel_id: Snowflake, before: Snowflake | None = None, limit: int = 50
    ) -> Response[threads.ThreadPaginationPayload]:
        route = Route(
            "GET",
            "/channels/{channel_id}/threads/archived/private",
            channel_id=channel_id,
        )

        params = {}
        if before:
            params["before"] = before
        params["limit"] = limit
        return self.request(route, params=params)

    def get_joined_private_archived_threads(
        self, channel_id: Snowflake, before: Snowflake | None = None, limit: int = 50
    ) -> Response[threads.ThreadPaginationPayload]:
        route = Route(
            "GET",
            "/channels/{channel_id}/users/@me/threads/archived/private",
            channel_id=channel_id,
        )
        params = {}
        if before:
            params["before"] = before
        params["limit"] = limit
        return self.request(route, params=params)

    def get_active_threads(
        self, guild_id: Snowflake
    ) -> Response[threads.ThreadPaginationPayload]:
        route = Route("GET", "/guilds/{guild_id}/threads/active", guild_id=guild_id)
        return self.request(route)

    def get_thread_members(
        self, channel_id: Snowflake
    ) -> Response[list[threads.ThreadMember]]:
        route = Route(
            "GET", "/channels/{channel_id}/thread-members", channel_id=channel_id
        )
        return self.request(route)

    # Webhook management

    def create_webhook(
        self,
        channel_id: Snowflake,
        *,
        name: str,
        avatar: bytes | None = None,
        reason: str | None = None,
    ) -> Response[webhook.Webhook]:
        payload: dict[str, Any] = {
            "name": name,
        }
        if avatar is not None:
            payload["avatar"] = avatar

        r = Route("POST", "/channels/{channel_id}/webhooks", channel_id=channel_id)
        return self.request(r, json=payload, reason=reason)

    def channel_webhooks(
        self, channel_id: Snowflake
    ) -> Response[list[webhook.Webhook]]:
        return self.request(
            Route("GET", "/channels/{channel_id}/webhooks", channel_id=channel_id)
        )

    def guild_webhooks(self, guild_id: Snowflake) -> Response[list[webhook.Webhook]]:
        return self.request(
            Route("GET", "/guilds/{guild_id}/webhooks", guild_id=guild_id)
        )

    def get_webhook(self, webhook_id: Snowflake) -> Response[webhook.Webhook]:
        return self.request(
            Route("GET", "/webhooks/{webhook_id}", webhook_id=webhook_id)
        )

    def follow_webhook(
        self,
        channel_id: Snowflake,
        webhook_channel_id: Snowflake,
        reason: str | None = None,
    ) -> Response[None]:
        payload = {
            "webhook_channel_id": str(webhook_channel_id),
        }
        return self.request(
            Route("POST", "/channels/{channel_id}/followers", channel_id=channel_id),
            json=payload,
            reason=reason,
        )

    # Guild management

    def get_guilds(
        self,
        limit: int,
        before: Snowflake | None = None,
        after: Snowflake | None = None,
        with_counts: bool = True,
    ) -> Response[list[guild.Guild]]:
        params: dict[str, Any] = {
            "limit": limit,
        }

        if before:
            params["before"] = before
        if after:
            params["after"] = after
        if with_counts:
            params["with_counts"] = int(with_counts)

        return self.request(Route("GET", "/users/@me/guilds"), params=params)

    def leave_guild(self, guild_id: Snowflake) -> Response[None]:
        return self.request(
            Route("DELETE", "/users/@me/guilds/{guild_id}", guild_id=guild_id)
        )

    def get_guild(
        self, guild_id: Snowflake, *, with_counts=True
    ) -> Response[guild.Guild]:
        params = {"with_counts": int(with_counts)}
        return self.request(
            Route("GET", "/guilds/{guild_id}", guild_id=guild_id), params=params
        )

    def delete_guild(self, guild_id: Snowflake) -> Response[None]:
        return self.request(Route("DELETE", "/guilds/{guild_id}", guild_id=guild_id))

    def create_guild(self, name: str, icon: str | None) -> Response[guild.Guild]:
        payload = {
            "name": name,
        }
        if icon:
            payload["icon"] = icon

        return self.request(Route("POST", "/guilds"), json=payload)

    def edit_guild(
        self, guild_id: Snowflake, *, reason: str | None = None, **fields: Any
    ) -> Response[guild.Guild]:
        valid_keys = (
            "name",
            "icon",
            "afk_timeout",
            "owner_id",
            "afk_channel_id",
            "splash",
            "discovery_splash",
            "features",
            "verification_level",
            "system_channel_id",
            "default_message_notifications",
            "description",
            "explicit_content_filter",
            "banner",
            "system_channel_flags",
            "rules_channel_id",
            "public_updates_channel_id",
            "preferred_locale",
            "premium_progress_bar_enabled",
        )

        payload = {k: v for k, v in fields.items() if k in valid_keys}

        return self.request(
            Route("PATCH", "/guilds/{guild_id}", guild_id=guild_id),
            json=payload,
            reason=reason,
        )

    def edit_guild_mfa(
        self, guild_id: Snowflake, required: bool, *, reason: str | None
    ) -> Response[guild.GuildMFAModify]:
        return self.request(
            Route("POST", "/guilds/{guild_id}/mfa", guild_id=guild_id),
            json={"level": int(required)},
            reason=reason,
        )

    def get_template(self, code: str) -> Response[template.Template]:
        return self.request(Route("GET", "/guilds/templates/{code}", code=code))

    def guild_templates(self, guild_id: Snowflake) -> Response[list[template.Template]]:
        return self.request(
            Route("GET", "/guilds/{guild_id}/templates", guild_id=guild_id)
        )

    def create_template(
        self, guild_id: Snowflake, payload: template.CreateTemplate
    ) -> Response[template.Template]:
        return self.request(
            Route("POST", "/guilds/{guild_id}/templates", guild_id=guild_id),
            json=payload,
        )

    def sync_template(
        self, guild_id: Snowflake, code: str
    ) -> Response[template.Template]:
        return self.request(
            Route(
                "PUT",
                "/guilds/{guild_id}/templates/{code}",
                guild_id=guild_id,
                code=code,
            )
        )

    def edit_template(
        self, guild_id: Snowflake, code: str, payload
    ) -> Response[template.Template]:
        valid_keys = (
            "name",
            "description",
        )
        payload = {k: v for k, v in payload.items() if k in valid_keys}
        return self.request(
            Route(
                "PATCH",
                "/guilds/{guild_id}/templates/{code}",
                guild_id=guild_id,
                code=code,
            ),
            json=payload,
        )

    def delete_template(self, guild_id: Snowflake, code: str) -> Response[None]:
        return self.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/templates/{code}",
                guild_id=guild_id,
                code=code,
            )
        )

    def create_from_template(
        self, code: str, name: str, icon: str | None
    ) -> Response[guild.Guild]:
        payload = {
            "name": name,
        }
        if icon:
            payload["icon"] = icon

        return self.request(
            Route("POST", "/guilds/templates/{code}", code=code), json=payload
        )

    def get_bans(
        self,
        guild_id: Snowflake,
        limit: int | None = None,
        before: Snowflake | None = None,
        after: Snowflake | None = None,
    ) -> Response[list[guild.Ban]]:
        params: dict[str, int | Snowflake] = {}

        if limit is not None:
            params["limit"] = limit
        if before is not None:
            params["before"] = before
        if after is not None:
            params["after"] = after

        return self.request(
            Route("GET", "/guilds/{guild_id}/bans", guild_id=guild_id), params=params
        )

    def get_ban(self, user_id: Snowflake, guild_id: Snowflake) -> Response[guild.Ban]:
        return self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/bans/{user_id}",
                guild_id=guild_id,
                user_id=user_id,
            )
        )

    def get_vanity_code(self, guild_id: Snowflake) -> Response[invite.VanityInvite]:
        return self.request(
            Route("GET", "/guilds/{guild_id}/vanity-url", guild_id=guild_id)
        )

    def get_all_guild_channels(
        self, guild_id: Snowflake
    ) -> Response[list[guild.GuildChannel]]:
        return self.request(
            Route("GET", "/guilds/{guild_id}/channels", guild_id=guild_id)
        )

    def get_members(
        self, guild_id: Snowflake, limit: int, after: Snowflake | None
    ) -> Response[list[member.MemberWithUser]]:
        params: dict[str, Any] = {
            "limit": limit,
        }
        if after:
            params["after"] = after

        r = Route("GET", "/guilds/{guild_id}/members", guild_id=guild_id)
        return self.request(r, params=params)

    def search_members(
        self,
        guild_id: Snowflake,
        query: str,
        limit: int,
    ) -> Response[list[member.MemberWithUser]]:
        params: dict[str, Any] = {
            "query": query,
            "limit": limit,
        }

        r = Route("GET", "/guilds/{guild_id}/members/search", guild_id=guild_id)
        return self.request(r, params=params)

    def get_member(
        self, guild_id: Snowflake, member_id: Snowflake
    ) -> Response[member.MemberWithUser]:
        return self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/members/{member_id}",
                guild_id=guild_id,
                member_id=member_id,
            )
        )

    def prune_members(
        self,
        guild_id: Snowflake,
        days: int,
        compute_prune_count: bool,
        roles: list[str],
        *,
        reason: str | None = None,
    ) -> Response[guild.GuildPrune]:
        payload: dict[str, Any] = {
            "days": days,
            "compute_prune_count": "true" if compute_prune_count else "false",
        }
        if roles:
            payload["include_roles"] = ", ".join(roles)

        return self.request(
            Route("POST", "/guilds/{guild_id}/prune", guild_id=guild_id),
            json=payload,
            reason=reason,
        )

    def estimate_pruned_members(
        self,
        guild_id: Snowflake,
        days: int,
        roles: list[str],
    ) -> Response[guild.GuildPrune]:
        params: dict[str, Any] = {
            "days": days,
        }
        if roles:
            params["include_roles"] = ", ".join(roles)

        return self.request(
            Route("GET", "/guilds/{guild_id}/prune", guild_id=guild_id), params=params
        )

    def get_sticker(self, sticker_id: Snowflake) -> Response[sticker.Sticker]:
        return self.request(
            Route("GET", "/stickers/{sticker_id}", sticker_id=sticker_id)
        )

    def list_premium_sticker_packs(self) -> Response[sticker.ListPremiumStickerPacks]:
        return self.request(Route("GET", "/sticker-packs"))

    def get_all_guild_stickers(
        self, guild_id: Snowflake
    ) -> Response[list[sticker.GuildSticker]]:
        return self.request(
            Route("GET", "/guilds/{guild_id}/stickers", guild_id=guild_id)
        )

    def get_guild_sticker(
        self, guild_id: Snowflake, sticker_id: Snowflake
    ) -> Response[sticker.GuildSticker]:
        return self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/stickers/{sticker_id}",
                guild_id=guild_id,
                sticker_id=sticker_id,
            )
        )

    def create_guild_sticker(
        self,
        guild_id: Snowflake,
        payload: sticker.CreateGuildSticker,
        file: File,
        reason: str,
    ) -> Response[sticker.GuildSticker]:
        initial_bytes = file.fp.read(16)

        try:
            mime_type = utils._get_mime_type_for_image(initial_bytes)
        except InvalidArgument:
            if initial_bytes.startswith(b"{"):
                mime_type = "application/json"
            else:
                mime_type = "application/octet-stream"
        finally:
            file.reset()

        form: list[dict[str, Any]] = [
            {
                "name": "file",
                "value": file.fp,
                "filename": file.filename,
                "content_type": mime_type,
            }
        ]

        for k, v in payload.items():
            form.append(
                {
                    "name": k,
                    "value": v,
                }
            )

        return self.request(
            Route("POST", "/guilds/{guild_id}/stickers", guild_id=guild_id),
            form=form,
            files=[file],
            reason=reason,
        )

    def modify_guild_sticker(
        self,
        guild_id: Snowflake,
        sticker_id: Snowflake,
        payload: sticker.EditGuildSticker,
        reason: str | None,
    ) -> Response[sticker.GuildSticker]:
        return self.request(
            Route(
                "PATCH",
                "/guilds/{guild_id}/stickers/{sticker_id}",
                guild_id=guild_id,
                sticker_id=sticker_id,
            ),
            json=payload,
            reason=reason,
        )

    def delete_guild_sticker(
        self, guild_id: Snowflake, sticker_id: Snowflake, reason: str | None
    ) -> Response[None]:
        return self.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/stickers/{sticker_id}",
                guild_id=guild_id,
                sticker_id=sticker_id,
            ),
            reason=reason,
        )

    def get_all_custom_emojis(self, guild_id: Snowflake) -> Response[list[emoji.Emoji]]:
        return self.request(
            Route("GET", "/guilds/{guild_id}/emojis", guild_id=guild_id)
        )

    def get_custom_emoji(
        self, guild_id: Snowflake, emoji_id: Snowflake
    ) -> Response[emoji.Emoji]:
        return self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/emojis/{emoji_id}",
                guild_id=guild_id,
                emoji_id=emoji_id,
            )
        )

    def create_custom_emoji(
        self,
        guild_id: Snowflake,
        name: str,
        image: bytes,
        *,
        roles: SnowflakeList | None = None,
        reason: str | None = None,
    ) -> Response[emoji.Emoji]:
        payload = {
            "name": name,
            "image": image,
            "roles": roles or [],
        }

        r = Route("POST", "/guilds/{guild_id}/emojis", guild_id=guild_id)
        return self.request(r, json=payload, reason=reason)

    def delete_custom_emoji(
        self,
        guild_id: Snowflake,
        emoji_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/guilds/{guild_id}/emojis/{emoji_id}",
            guild_id=guild_id,
            emoji_id=emoji_id,
        )
        return self.request(r, reason=reason)

    def edit_custom_emoji(
        self,
        guild_id: Snowflake,
        emoji_id: Snowflake,
        *,
        payload: dict[str, Any],
        reason: str | None = None,
    ) -> Response[emoji.Emoji]:
        r = Route(
            "PATCH",
            "/guilds/{guild_id}/emojis/{emoji_id}",
            guild_id=guild_id,
            emoji_id=emoji_id,
        )
        return self.request(r, json=payload, reason=reason)

    def get_all_application_emojis(
        self, application_id: Snowflake
    ) -> Response[list[emoji.Emoji]]:
        return self.request(
            Route(
                "GET",
                "/applications/{application_id}/emojis",
                application_id=application_id,
            )
        )

    def get_application_emoji(
        self, application_id: Snowflake, emoji_id: Snowflake
    ) -> Response[emoji.Emoji]:
        return self.request(
            Route(
                "GET",
                "/applications/{application_id}/emojis/{emoji_id}",
                application_id=application_id,
                emoji_id=emoji_id,
            )
        )

    def create_application_emoji(
        self,
        application_id: Snowflake,
        name: str,
        image: bytes,
    ) -> Response[emoji.Emoji]:
        payload = {
            "name": name,
            "image": image,
        }

        r = Route(
            "POST",
            "/applications/{application_id}/emojis",
            application_id=application_id,
        )
        return self.request(r, json=payload)

    def delete_application_emoji(
        self,
        application_id: Snowflake,
        emoji_id: Snowflake,
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/applications/{application_id}/emojis/{emoji_id}",
            application_id=application_id,
            emoji_id=emoji_id,
        )
        return self.request(r)

    def edit_application_emoji(
        self,
        application_id: Snowflake,
        emoji_id: Snowflake,
        *,
        payload: dict[str, Any],
    ) -> Response[emoji.Emoji]:
        r = Route(
            "PATCH",
            "/applications/{application_id}/emojis/{emoji_id}",
            application_id=application_id,
            emoji_id=emoji_id,
        )
        return self.request(r, json=payload)

    def get_all_integrations(
        self, guild_id: Snowflake
    ) -> Response[list[integration.Integration]]:
        r = Route("GET", "/guilds/{guild_id}/integrations", guild_id=guild_id)

        return self.request(r)

    def create_integration(
        self, guild_id: Snowflake, type: integration.IntegrationType, id: int
    ) -> Response[None]:
        payload = {
            "type": type,
            "id": id,
        }

        r = Route("POST", "/guilds/{guild_id}/integrations", guild_id=guild_id)
        return self.request(r, json=payload)

    def edit_integration(
        self, guild_id: Snowflake, integration_id: Snowflake, **payload: Any
    ) -> Response[None]:
        r = Route(
            "PATCH",
            "/guilds/{guild_id}/integrations/{integration_id}",
            guild_id=guild_id,
            integration_id=integration_id,
        )

        return self.request(r, json=payload)

    def sync_integration(
        self, guild_id: Snowflake, integration_id: Snowflake
    ) -> Response[None]:
        r = Route(
            "POST",
            "/guilds/{guild_id}/integrations/{integration_id}/sync",
            guild_id=guild_id,
            integration_id=integration_id,
        )

        return self.request(r)

    def delete_integration(
        self,
        guild_id: Snowflake,
        integration_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/guilds/{guild_id}/integrations/{integration_id}",
            guild_id=guild_id,
            integration_id=integration_id,
        )

        return self.request(r, reason=reason)

    def get_audit_logs(
        self,
        guild_id: Snowflake,
        limit: int = 100,
        before: Snowflake | None = None,
        after: Snowflake | None = None,
        user_id: Snowflake | None = None,
        action_type: AuditLogAction | None = None,
    ) -> Response[audit_log.AuditLog]:
        params: dict[str, Any] = {"limit": limit}
        if before is not None:
            params["before"] = before
        if after is not None:
            params["after"] = after
        if user_id:
            params["user_id"] = user_id
        if action_type:
            params["action_type"] = action_type

        r = Route("GET", "/guilds/{guild_id}/audit-logs", guild_id=guild_id)
        return self.request(r, params=params)

    def get_widget(self, guild_id: Snowflake) -> Response[widget.Widget]:
        return self.request(
            Route("GET", "/guilds/{guild_id}/widget.json", guild_id=guild_id)
        )

    def edit_widget(
        self, guild_id: Snowflake, payload
    ) -> Response[widget.WidgetSettings]:
        return self.request(
            Route("PATCH", "/guilds/{guild_id}/widget", guild_id=guild_id), json=payload
        )

    # Invite management

    def create_invite(
        self,
        channel_id: Snowflake,
        *,
        reason: str | None = None,
        max_age: int = 0,
        max_uses: int = 0,
        temporary: bool = False,
        unique: bool = True,
        target_type: invite.InviteTargetType | None = None,
        target_user_id: Snowflake | None = None,
        target_application_id: Snowflake | None = None,
    ) -> Response[invite.Invite]:
        r = Route("POST", "/channels/{channel_id}/invites", channel_id=channel_id)
        payload = {
            "max_age": max_age,
            "max_uses": max_uses,
            "temporary": temporary,
            "unique": unique,
        }

        if target_type:
            payload["target_type"] = target_type

        if target_user_id:
            payload["target_user_id"] = target_user_id

        if target_application_id:
            payload["target_application_id"] = str(target_application_id)

        return self.request(r, reason=reason, json=payload)

    def get_invite(
        self,
        invite_id: str,
        *,
        with_counts: bool = True,
        with_expiration: bool = True,
        guild_scheduled_event_id: int | None = None,
    ) -> Response[invite.Invite]:
        params = {
            "with_counts": int(with_counts),
            "with_expiration": int(with_expiration),
        }

        if guild_scheduled_event_id is not None:
            params["guild_scheduled_event_id"] = int(guild_scheduled_event_id)

        return self.request(
            Route("GET", "/invites/{invite_id}", invite_id=invite_id), params=params
        )

    def invites_from(self, guild_id: Snowflake) -> Response[list[invite.Invite]]:
        return self.request(
            Route("GET", "/guilds/{guild_id}/invites", guild_id=guild_id)
        )

    def invites_from_channel(
        self, channel_id: Snowflake
    ) -> Response[list[invite.Invite]]:
        return self.request(
            Route("GET", "/channels/{channel_id}/invites", channel_id=channel_id)
        )

    def delete_invite(
        self, invite_id: str, *, reason: str | None = None
    ) -> Response[None]:
        return self.request(
            Route("DELETE", "/invites/{invite_id}", invite_id=invite_id), reason=reason
        )

    # Role management

    def get_roles(self, guild_id: Snowflake) -> Response[list[role.Role]]:
        return self.request(Route("GET", "/guilds/{guild_id}/roles", guild_id=guild_id))

    def get_role(self, guild_id: Snowflake, role_id: Snowflake) -> Response[role.Role]:
        return self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/roles/{role_id}",
                guild_id=guild_id,
                role_id=role_id,
            )
        )

    def edit_role(
        self,
        guild_id: Snowflake,
        role_id: Snowflake,
        *,
        reason: str | None = None,
        **fields: Any,
    ) -> Response[role.Role]:
        r = Route(
            "PATCH",
            "/guilds/{guild_id}/roles/{role_id}",
            guild_id=guild_id,
            role_id=role_id,
        )
        valid_keys = (
            "name",
            "permissions",
            "color",
            "colors",
            "hoist",
            "mentionable",
            "icon",
            "unicode_emoji",
        )
        payload = {k: v for k, v in fields.items() if k in valid_keys}
        return self.request(r, json=payload, reason=reason)

    def delete_role(
        self, guild_id: Snowflake, role_id: Snowflake, *, reason: str | None = None
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/guilds/{guild_id}/roles/{role_id}",
            guild_id=guild_id,
            role_id=role_id,
        )
        return self.request(r, reason=reason)

    def replace_roles(
        self,
        user_id: Snowflake,
        guild_id: Snowflake,
        role_ids: list[int],
        *,
        reason: str | None = None,
    ) -> Response[member.MemberWithUser]:
        return self.edit_member(
            guild_id=guild_id, user_id=user_id, roles=role_ids, reason=reason
        )

    def create_role(
        self, guild_id: Snowflake, *, reason: str | None = None, **fields: Any
    ) -> Response[role.Role]:
        r = Route("POST", "/guilds/{guild_id}/roles", guild_id=guild_id)
        return self.request(r, json=fields, reason=reason)

    def move_role_position(
        self,
        guild_id: Snowflake,
        positions: list[guild.RolePositionUpdate],
        *,
        reason: str | None = None,
    ) -> Response[list[role.Role]]:
        r = Route("PATCH", "/guilds/{guild_id}/roles", guild_id=guild_id)
        return self.request(r, json=positions, reason=reason)

    def add_role(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        role_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> Response[None]:
        r = Route(
            "PUT",
            "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
            guild_id=guild_id,
            user_id=user_id,
            role_id=role_id,
        )
        return self.request(r, reason=reason)

    def remove_role(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        role_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
            guild_id=guild_id,
            user_id=user_id,
            role_id=role_id,
        )
        return self.request(r, reason=reason)

    def edit_channel_permissions(
        self,
        channel_id: Snowflake,
        target: Snowflake,
        allow: int | str,
        deny: int | str,
        type: channel.OverwriteType,
        *,
        reason: str | None = None,
    ) -> Response[None]:
        payload = {"id": target, "allow": allow, "deny": deny, "type": type}
        r = Route(
            "PUT",
            "/channels/{channel_id}/permissions/{target}",
            channel_id=channel_id,
            target=target,
        )
        return self.request(r, json=payload, reason=reason)

    def delete_channel_permissions(
        self,
        channel_id: Snowflake,
        target: channel.OverwriteType,
        *,
        reason: str | None = None,
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/channels/{channel_id}/permissions/{target}",
            channel_id=channel_id,
            target=target,
        )
        return self.request(r, reason=reason)

    # Welcome Screen

    def get_welcome_screen(
        self, guild_id: Snowflake
    ) -> Response[welcome_screen.WelcomeScreen]:
        return self.request(
            Route("GET", "/guilds/{guild_id}/welcome-screen", guild_id=guild_id)
        )

    def edit_welcome_screen(
        self, guild_id: Snowflake, payload: Any, *, reason: str | None = None
    ) -> Response[welcome_screen.WelcomeScreen]:
        keys = (
            "description",
            "welcome_channels",
            "enabled",
        )
        payload = {key: val for key, val in payload.items() if key in keys}
        return self.request(
            Route("PATCH", "/guilds/{guild_id}/welcome-screen", guild_id=guild_id),
            json=payload,
            reason=reason,
        )

    # Voice management

    def move_member(
        self,
        user_id: Snowflake,
        guild_id: Snowflake,
        channel_id: Snowflake,
        *,
        reason: str | None = None,
    ) -> Response[member.MemberWithUser]:
        return self.edit_member(
            guild_id=guild_id, user_id=user_id, channel_id=channel_id, reason=reason
        )

    def set_voice_channel_status(
        self, channel_id: Snowflake, status: str | None, *, reason: str | None = None
    ) -> Response[None]:
        payload = {"status": status}
        r = Route("PUT", "/channels/{channel_id}/voice-status", channel_id=channel_id)
        return self.request(r, json=payload, reason=reason)

    # Stage instance management

    def get_stage_instance(
        self, channel_id: Snowflake
    ) -> Response[channel.StageInstance]:
        return self.request(
            Route("GET", "/stage-instances/{channel_id}", channel_id=channel_id)
        )

    def create_stage_instance(
        self, *, reason: str | None, **payload: Any
    ) -> Response[channel.StageInstance]:
        valid_keys = (
            "channel_id",
            "topic",
            "privacy_level",
            "send_start_notification",
        )
        payload = {k: v for k, v in payload.items() if k in valid_keys}

        if payload.get("send_start_notification") is not None:
            payload["send_start_notification"] = int(payload["send_start_notification"])

        return self.request(
            Route("POST", "/stage-instances"), json=payload, reason=reason
        )

    def edit_stage_instance(
        self, channel_id: Snowflake, *, reason: str | None = None, **payload: Any
    ) -> Response[None]:
        valid_keys = (
            "topic",
            "privacy_level",
        )
        payload = {k: v for k, v in payload.items() if k in valid_keys}

        return self.request(
            Route("PATCH", "/stage-instances/{channel_id}", channel_id=channel_id),
            json=payload,
            reason=reason,
        )

    def delete_stage_instance(
        self, channel_id: Snowflake, *, reason: str | None = None
    ) -> Response[None]:
        return self.request(
            Route("DELETE", "/stage-instances/{channel_id}", channel_id=channel_id),
            reason=reason,
        )

    # Guild scheduled events management

    def get_scheduled_events(
        self, guild_id: Snowflake, with_user_count: bool = True
    ) -> Response[list[scheduled_events.ScheduledEvent]]:
        params = {
            "with_user_count": int(with_user_count),
        }

        return self.request(
            Route("GET", "/guilds/{guild_id}/scheduled-events", guild_id=guild_id),
            params=params,
        )

    def get_scheduled_event(
        self, guild_id: Snowflake, event_id: Snowflake, with_user_count: bool = True
    ) -> Response[scheduled_events.ScheduledEvent]:
        params = {
            "with_user_count": int(with_user_count),
        }

        return self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/scheduled-events/{event_id}",
                guild_id=guild_id,
                event_id=event_id,
            ),
            params=params,
        )

    def create_scheduled_event(
        self, guild_id: Snowflake, reason: str | None = None, **payload: Any
    ) -> Response[scheduled_events.ScheduledEvent]:
        valid_keys = (
            "channel_id",
            "name",
            "privacy_level",
            "scheduled_start_time",
            "scheduled_end_time",
            "description",
            "entity_type",
            "entity_metadata",
            "image",
        )
        payload = {k: v for k, v in payload.items() if k in valid_keys}

        return self.request(
            Route("POST", "/guilds/{guild_id}/scheduled-events", guild_id=guild_id),
            json=payload,
            reason=reason,
        )

    def delete_scheduled_event(
        self, guild_id: Snowflake, event_id: Snowflake
    ) -> Response[None]:
        return self.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/scheduled-events/{event_id}",
                guild_id=guild_id,
                event_id=event_id,
            )
        )

    def edit_scheduled_event(
        self,
        guild_id: Snowflake,
        event_id: Snowflake,
        reason: str | None = None,
        **payload: Any,
    ) -> Response[scheduled_events.ScheduledEvent]:
        valid_keys = (
            "channel_id",
            "name",
            "privacy_level",
            "scheduled_start_time",
            "scheduled_end_time",
            "description",
            "entity_type",
            "status",
            "entity_metadata",
            "image",
        )
        payload = {k: v for k, v in payload.items() if k in valid_keys}

        return self.request(
            Route(
                "PATCH",
                "/guilds/{guild_id}/scheduled-events/{event_id}",
                guild_id=guild_id,
                event_id=event_id,
            ),
            json=payload,
            reason=reason,
        )

    def get_scheduled_event_users(
        self,
        guild_id: Snowflake,
        event_id: Snowflake,
        limit: int,
        with_member: bool = False,
        before: Snowflake = None,
        after: Snowflake = None,
    ) -> Response[list[scheduled_events.ScheduledEventSubscriber]]:
        params = {
            "limit": int(limit),
            "with_member": int(with_member),
        }

        if before is not None:
            params["before"] = int(before)

        if after is not None:
            params["after"] = int(after)

        return self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/scheduled-events/{event_id}/users",
                guild_id=guild_id,
                event_id=event_id,
            ),
            params=params,
        )

    # Application commands (global)

    def get_global_commands(
        self,
        application_id: Snowflake,
        *,
        with_localizations: bool = True,
        locale: str = None,
    ) -> Response[list[interactions.ApplicationCommand]]:
        params = {"with_localizations": int(with_localizations)}

        return self.request(
            Route(
                "GET",
                "/applications/{application_id}/commands",
                application_id=application_id,
            ),
            params=params,
            locale=locale,
        )

    def get_global_command(
        self,
        application_id: Snowflake,
        command_id: Snowflake,
        locale: str = None,
    ) -> Response[interactions.ApplicationCommand]:
        r = Route(
            "GET",
            "/applications/{application_id}/commands/{command_id}",
            application_id=application_id,
            command_id=command_id,
        )
        return self.request(r, locale=locale)

    def upsert_global_command(
        self, application_id: Snowflake, payload
    ) -> Response[interactions.ApplicationCommand]:
        r = Route(
            "POST",
            "/applications/{application_id}/commands",
            application_id=application_id,
        )
        return self.request(r, json=payload)

    def edit_global_command(
        self,
        application_id: Snowflake,
        command_id: Snowflake,
        payload: interactions.EditApplicationCommand,
    ) -> Response[interactions.ApplicationCommand]:
        valid_keys = (
            "name",
            "description",
            "options",
        )
        payload = {k: v for k, v in payload.items() if k in valid_keys}  # type: ignore
        r = Route(
            "PATCH",
            "/applications/{application_id}/commands/{command_id}",
            application_id=application_id,
            command_id=command_id,
        )
        return self.request(r, json=payload)

    def delete_global_command(
        self, application_id: Snowflake, command_id: Snowflake
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/applications/{application_id}/commands/{command_id}",
            application_id=application_id,
            command_id=command_id,
        )
        return self.request(r)

    def bulk_upsert_global_commands(
        self, application_id: Snowflake, payload
    ) -> Response[list[interactions.ApplicationCommand]]:
        r = Route(
            "PUT",
            "/applications/{application_id}/commands",
            application_id=application_id,
        )
        return self.request(r, json=payload)

    # Application commands (guild)

    def get_guild_commands(
        self, application_id: Snowflake, guild_id: Snowflake
    ) -> Response[list[interactions.ApplicationCommand]]:
        r = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands",
            application_id=application_id,
            guild_id=guild_id,
        )
        return self.request(r)

    def get_guild_command(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
    ) -> Response[interactions.ApplicationCommand]:
        r = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )
        return self.request(r)

    def upsert_guild_command(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        payload: interactions.EditApplicationCommand,
    ) -> Response[interactions.ApplicationCommand]:
        r = Route(
            "POST",
            "/applications/{application_id}/guilds/{guild_id}/commands",
            application_id=application_id,
            guild_id=guild_id,
        )
        return self.request(r, json=payload)

    def edit_guild_command(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
        payload: interactions.EditApplicationCommand,
    ) -> Response[interactions.ApplicationCommand]:
        valid_keys = (
            "name",
            "description",
            "options",
        )
        payload = {k: v for k, v in payload.items() if k in valid_keys}  # type: ignore
        r = Route(
            "PATCH",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )
        return self.request(r, json=payload)

    def delete_guild_command(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )
        return self.request(r)

    def bulk_upsert_guild_commands(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        payload: list[interactions.EditApplicationCommand],
    ) -> Response[list[interactions.ApplicationCommand]]:
        r = Route(
            "PUT",
            "/applications/{application_id}/guilds/{guild_id}/commands",
            application_id=application_id,
            guild_id=guild_id,
        )
        return self.request(r, json=payload)

    # Guild Automod Rules

    def get_auto_moderation_rules(
        self,
        guild_id: Snowflake,
    ) -> Response[list[automod.AutoModRule]]:
        r = Route(
            "GET",
            "/guilds/{guild_id}/auto-moderation/rules",
            guild_id=guild_id,
        )
        return self.request(r)

    def get_auto_moderation_rule(
        self,
        guild_id: Snowflake,
        rule_id: Snowflake,
    ) -> Response[automod.AutoModRule]:
        r = Route(
            "GET",
            "/guilds/{guild_id}/auto-moderation/rules/{rule_id}",
            guild_id=guild_id,
            rule_id=rule_id,
        )
        return self.request(r)

    def create_auto_moderation_rule(
        self,
        guild_id: Snowflake,
        payload: automod.CreateAutoModRule,
        reason: str | None = None,
    ) -> Response[automod.AutoModRule]:
        r = Route(
            "POST",
            "/guilds/{guild_id}/auto-moderation/rules",
            guild_id=guild_id,
        )
        return self.request(r, json=payload, reason=reason)

    def edit_auto_moderation_rule(
        self,
        guild_id: Snowflake,
        rule_id: Snowflake,
        payload: automod.EditAutoModRule,
        reason: str | None = None,
    ) -> Response[automod.AutoModRule]:
        r = Route(
            "PATCH",
            "/guilds/{guild_id}/auto-moderation/rules/{rule_id}",
            guild_id=guild_id,
            rule_id=rule_id,
        )
        return self.request(r, json=payload, reason=reason)

    def delete_auto_moderation_rule(
        self,
        guild_id: Snowflake,
        rule_id: Snowflake,
        reason: str | None = None,
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/guilds/{guild_id}/auto-moderation/rules/{rule_id}",
            guild_id=guild_id,
            rule_id=rule_id,
        )
        return self.request(r, reason=reason)

    # Interaction responses

    def _edit_webhook_helper(
        self,
        route: Route,
        file: File | None = None,
        content: str | None = None,
        embeds: list[embed.Embed] | None = None,
        allowed_mentions: message.AllowedMentions | None = None,
    ):
        payload: dict[str, Any] = {}
        if content:
            payload["content"] = content
        if embeds:
            payload["embeds"] = embeds
        if allowed_mentions:
            payload["allowed_mentions"] = allowed_mentions

        form: list[dict[str, Any]] = [
            {
                "name": "payload_json",
                "value": utils._to_json(payload),
            }
        ]

        if file:
            form.append(
                {
                    "name": "file",
                    "value": file.fp,
                    "filename": file.filename,
                    "content_type": "application/octet-stream",
                }
            )

        return self.request(route, form=form, files=[file] if file else None)

    def create_interaction_response(
        self,
        interaction_id: Snowflake,
        token: str,
        *,
        type: InteractionResponseType,
        data: interactions.InteractionApplicationCommandCallbackData | None = None,
    ) -> Response[None]:
        r = Route(
            "POST",
            "/interactions/{interaction_id}/{interaction_token}/callback",
            interaction_id=interaction_id,
            interaction_token=token,
        )
        payload: dict[str, Any] = {
            "type": type,
        }

        if data is not None:
            payload["data"] = data

        return self.request(r, json=payload)

    def get_original_interaction_response(
        self,
        application_id: Snowflake,
        token: str,
    ) -> Response[message.Message]:
        r = Route(
            "GET",
            "/webhooks/{application_id}/{interaction_token}/messages/@original",
            application_id=application_id,
            interaction_token=token,
        )
        return self.request(r)

    def edit_original_interaction_response(
        self,
        application_id: Snowflake,
        token: str,
        file: File | None = None,
        content: str | None = None,
        embeds: list[embed.Embed] | None = None,
        allowed_mentions: message.AllowedMentions | None = None,
    ) -> Response[message.Message]:
        r = Route(
            "PATCH",
            "/webhooks/{application_id}/{interaction_token}/messages/@original",
            application_id=application_id,
            interaction_token=token,
        )
        return self._edit_webhook_helper(
            r,
            file=file,
            content=content,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
        )

    def delete_original_interaction_response(
        self, application_id: Snowflake, token: str
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/webhooks/{application_id}/{interaction_token}/messages/@original",
            application_id=application_id,
            interaction_token=token,
        )
        return self.request(r)

    def create_followup_message(
        self,
        application_id: Snowflake,
        token: str,
        files: list[File] | None = None,
        content: str | None = None,
        tts: bool = False,
        embeds: list[embed.Embed] | None = None,
        allowed_mentions: message.AllowedMentions | None = None,
    ) -> Response[message.Message]:
        r = Route(
            "POST",
            "/webhooks/{application_id}/{interaction_token}",
            application_id=application_id,
            interaction_token=token,
        )
        return self.send_multipart_helper(
            r,
            content=content,
            files=files,
            tts=tts,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
        )

    def edit_followup_message(
        self,
        application_id: Snowflake,
        token: str,
        message_id: Snowflake,
        file: File | None = None,
        content: str | None = None,
        embeds: list[embed.Embed] | None = None,
        allowed_mentions: message.AllowedMentions | None = None,
    ) -> Response[message.Message]:
        r = Route(
            "PATCH",
            "/webhooks/{application_id}/{interaction_token}/messages/{message_id}",
            application_id=application_id,
            interaction_token=token,
            message_id=message_id,
        )
        return self._edit_webhook_helper(
            r,
            file=file,
            content=content,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
        )

    def delete_followup_message(
        self, application_id: Snowflake, token: str, message_id: Snowflake
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/webhooks/{application_id}/{interaction_token}/messages/{message_id}",
            application_id=application_id,
            interaction_token=token,
            message_id=message_id,
        )
        return self.request(r)

    # Application commands (permissions)

    def get_guild_application_command_permissions(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
    ) -> Response[list[interactions.GuildApplicationCommandPermissions]]:
        r = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands/permissions",
            application_id=application_id,
            guild_id=guild_id,
        )
        return self.request(r)

    def get_application_command_permissions(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
    ) -> Response[interactions.GuildApplicationCommandPermissions]:
        r = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )
        return self.request(r)

    def edit_application_command_permissions(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
        payload: interactions.BaseGuildApplicationCommandPermissions,
    ) -> Response[None]:
        r = Route(
            "PUT",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )
        return self.request(r, json=payload)

    def bulk_edit_guild_application_command_permissions(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        payload: list[interactions.PartialGuildApplicationCommandPermissions],
    ) -> Response[None]:
        r = Route(
            "PUT",
            "/applications/{application_id}/guilds/{guild_id}/commands/permissions",
            application_id=application_id,
            guild_id=guild_id,
        )
        return self.request(r, json=payload)

    # Application Role Connections

    def get_application_role_connection_metadata_records(
        self,
        application_id: Snowflake,
    ) -> Response[list[application_role_connection.ApplicationRoleConnectionMetadata]]:
        r = Route(
            "GET",
            "/applications/{application_id}/role-connections/metadata",
            application_id=application_id,
        )
        return self.request(r)

    def update_application_role_connection_metadata_records(
        self,
        application_id: Snowflake,
        payload: list[application_role_connection.ApplicationRoleConnectionMetadata],
    ) -> Response[list[application_role_connection.ApplicationRoleConnectionMetadata]]:
        r = Route(
            "PUT",
            "/applications/{application_id}/role-connections/metadata",
            application_id=application_id,
        )
        return self.request(r, json=payload)

    # Monetization

    def list_skus(
        self,
        application_id: Snowflake,
    ) -> Response[list[monetization.SKU]]:
        r = Route(
            "GET",
            "/applications/{application_id}/skus",
            application_id=application_id,
        )
        return self.request(r)

    def list_entitlements(
        self,
        application_id: Snowflake,
        *,
        user_id: Snowflake | None = None,
        sku_ids: list[Snowflake] | None = None,
        before: Snowflake | None = None,
        after: Snowflake | None = None,
        limit: int | None = None,
        guild_id: Snowflake | None = None,
        exclude_ended: bool | None = None,
    ) -> Response[list[monetization.Entitlement]]:
        params: dict[str, Any] = {}
        if user_id is not None:
            params["user_id"] = user_id
        if sku_ids is not None:
            params["sku_ids"] = ",".join(str(sku_id) for sku_id in sku_ids)
        if before is not None:
            params["before"] = before
        if after is not None:
            params["after"] = after
        if limit is not None:
            params["limit"] = limit
        if guild_id is not None:
            params["guild_id"] = guild_id
        if exclude_ended is not None:
            params["exclude_ended"] = int(exclude_ended)

        r = Route(
            "GET",
            "/applications/{application_id}/entitlements",
            application_id=application_id,
        )
        return self.request(r, params=params)

    def consume_entitlement(
        self,
        application_id: Snowflake,
        entitlement_id: Snowflake,
    ) -> Response[None]:
        r = Route(
            "POST",
            "/applications/{application_id}/entitlements/{entitlement_id}/consume",
            application_id=application_id,
            entitlement_id=entitlement_id,
        )
        return self.request(r)

    def create_test_entitlement(
        self,
        application_id: Snowflake,
        payload: monetization.CreateTestEntitlementPayload,
    ) -> Response[monetization.Entitlement]:
        r = Route(
            "POST",
            "/applications/{application_id}/entitlements",
            application_id=application_id,
        )
        return self.request(r, json=payload)

    def delete_test_entitlement(
        self,
        application_id: Snowflake,
        entitlement_id: Snowflake,
    ) -> Response[None]:
        r = Route(
            "DELETE",
            "/applications/{application_id}/entitlements/{entitlement_id}",
            application_id=application_id,
            entitlement_id=entitlement_id,
        )
        return self.request(r)

    def list_sku_subscriptions(
        self,
        sku_id: Snowflake,
        *,
        before: Snowflake | None = None,
        after: Snowflake | None = None,
        limit: int = 50,
        user_id: Snowflake | None = None,
    ) -> Response[list[monetization.Subscription]]:
        params: dict[str, Any] = {}
        if before is not None:
            params["before"] = before
        if after is not None:
            params["after"] = after
        if limit is not None:
            params["limit"] = limit
        if user_id is not None:
            params["user_id"] = user_id
        return self.request(
            Route("GET", "/skus/{sku_id}/subscriptions", sku_id=sku_id),
            params=params,
        )

    def get_subscription(
        self,
        sku_id: Snowflake,
        subscription_id: Snowflake,
    ) -> Response[monetization.Subscription]:
        return self.request(
            Route(
                "GET",
                "/skus/{sku_id}/subscriptions/{subscription_id}",
                sku_id=sku_id,
                subscription_id=subscription_id,
            )
        )

    # Onboarding

    def get_onboarding(self, guild_id: Snowflake) -> Response[onboarding.Onboarding]:
        return self.request(
            Route("GET", "/guilds/{guild_id}/onboarding", guild_id=guild_id)
        )

    def edit_onboarding(
        self, guild_id: Snowflake, payload: Any, *, reason: str | None = None
    ) -> Response[onboarding.Onboarding]:
        keys = (
            "prompts",
            "default_channel_ids",
            "enabled",
            "mode",
        )
        payload = {key: val for key, val in payload.items() if key in keys}
        return self.request(
            Route("PUT", "/guilds/{guild_id}/onboarding", guild_id=guild_id),
            json=payload,
            reason=reason,
        )

    # Polls

    def expire_poll(
        self, channel_id: Snowflake, message_id: Snowflake
    ) -> Response[message.Message]:
        return self.request(
            Route(
                "POST",
                "/channels/{channel_id}/polls/{message_id}/expire",
                channel_id=channel_id,
                message_id=message_id,
            )
        )

    def get_answer_voters(
        self,
        channel_id: Snowflake,
        message_id: Snowflake,
        answer_id: int,
        limit: int,
        after: Snowflake | None = None,
    ) -> Response[list[user.User]]:
        r = Route(
            "GET",
            "/channels/{channel_id}/polls/{message_id}/answers/{answer_id}",
            channel_id=channel_id,
            message_id=message_id,
            answer_id=answer_id,
        )

        params: dict[str, Any] = {
            "limit": limit,
        }
        if after:
            params["after"] = after
        return self.request(r, params=params)

    # Misc

    def application_info(self) -> Response[appinfo.AppInfo]:
        return self.request(Route("GET", "/oauth2/applications/@me"))

    def get_application(
        self, application_id: Snowflake, /
    ) -> Response[appinfo.PartialAppInfo]:
        return self.request(
            Route(
                "GET",
                "/applications/{application_id}/rpc",
                application_id=application_id,
            )
        )

    async def get_gateway(self, *, encoding: str = "json", zlib: bool = True) -> str:
        try:
            data = await self.request(Route("GET", "/gateway"))
        except HTTPException as exc:
            raise GatewayNotFound() from exc
        if zlib:
            value = "{0}?encoding={1}&v={2}&compress=zlib-stream"
        else:
            value = "{0}?encoding={1}&v={2}"
        return value.format(data["url"], encoding, API_VERSION)

    async def get_bot_gateway(
        self, *, encoding: str = "json", zlib: bool = True
    ) -> tuple[int, str]:
        try:
            data = await self.request(Route("GET", "/gateway/bot"))
        except HTTPException as exc:
            raise GatewayNotFound() from exc

        if zlib:
            value = "{0}?encoding={1}&v={2}&compress=zlib-stream"
        else:
            value = "{0}?encoding={1}&v={2}"
        return data["shards"], value.format(data["url"], encoding, API_VERSION)

    def get_user(self, user_id: Snowflake) -> Response[user.User]:
        return self.request(Route("GET", "/users/{user_id}", user_id=user_id))
