from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Literal, Optional, TypeVar, Union, cast, overload
from typing_extensions import ParamSpec

import aiohttp

from .errors import RevoltError
from .channel import (DMChannel, GroupDMChannel, SavedMessageChannel,
                      TextChannel, VoiceChannel, channel_factory)
from .http import HttpClient
from .invite import Invite
from .message import Message
from .state import State
from .utils import Missing, Ulid
from .websocket import WebsocketHandler
from .emoji import Emoji
from .server import Server
from .user import User

try:
    import ujson as json
except ImportError:
    import json

if TYPE_CHECKING:
    from .channel import Channel
    from .file import File
    from .types import ApiInfo

__all__ = ("Client",)

logger: logging.Logger = logging.getLogger("revolt")

P = ParamSpec("P")
R = TypeVar("R")

class Client:
    """The client for interacting with revolt

    Parameters
    -----------
    session: :class:`aiohttp.ClientSession`
        The aiohttp session to use for http request and the websocket
    token: :class:`str`
        The bots token
    api_url: :class:`str`
        The api url for the revolt instance you are connecting to, by default it uses the offical instance hosted at revolt.chat
    max_messages: :class:`int`
        The max amount of messages stored in the cache, by default this is 5k
    """

    def __init__(self, session: aiohttp.ClientSession, token: str, *, api_url: str = "https://api.revolt.chat", max_messages: int = 5000, bot: bool = True):
        self.session: aiohttp.ClientSession = session
        self.token: str = token
        self.api_url: str = api_url
        self.max_messages: int = max_messages
        self.bot: bool = bot

        self.api_info: ApiInfo
        self.http: HttpClient
        self.state: State
        self.websocket: WebsocketHandler

        self.temp_listeners: dict[str, list[tuple[Callable[..., bool], asyncio.Future[Any]]]] = {}
        self.listeners: dict[str, list[Callable[..., Coroutine[Any, Any, Any]]]] = {}

        super().__init__()

    def dispatch(self, event: str, *args: Any) -> None:
        """Dispatch an event, this is typically used for testing and internals.

        Parameters
        ----------
        event: class:`str`
            The name of the event to dispatch, not including `on_`
        args: :class:`Any`
            The arguments passed to the event
        """
        for check, future in self.temp_listeners.pop(event, []):
            if check(*args):
                if len(args) == 1:
                    future.set_result(args[0])
                else:
                    future.set_result(args)

        for listener in self.listeners.get(event, []):
            asyncio.create_task(listener(*args))

        if func := getattr(self, f"on_{event}", None):
            asyncio.create_task(func(*args))

    async def get_api_info(self) -> ApiInfo:
        async with self.session.get(self.api_url) as resp:
            text = await resp.text()

            try:
                return json.loads(text)
            except:
                raise RevoltError(f"Cant fetch api info:\n{text}")

    async def start(self) -> None:
        """Starts the client"""
        api_info = await self.get_api_info()

        self.api_info = api_info
        self.http = HttpClient(self.session, self.token, self.api_url, self.api_info, self.bot)
        self.state = State(self.http, api_info, self.max_messages)
        self.websocket = WebsocketHandler(self.session, self.token, api_info["ws"], self.dispatch, self.state)

        await self.websocket.start()

    async def stop(self) -> None:
        await self.websocket.websocket.close()

    def get_user(self, id: str) -> User:
        """Gets a user from the cache

        Parameters
        -----------
        id: :class:`str`
            The id of the user

        Returns
        --------
        :class:`User`
            The user
        """
        return self.state.get_user(id)

    def get_channel(self, id: str) -> Channel:
        """Gets a channel from the cache

        Parameters
        -----------
        id: :class:`str`
            The id of the channel

        Returns
        --------
        :class:`Channel`
            The channel
        """
        return self.state.get_channel(id)

    def get_server(self, id: str) -> Server:
        """Gets a server from the cache

        Parameters
        -----------
        id: :class:`str`
            The id of the server

        Returns
        --------
        :class:`Server`
            The server
        """
        return self.state.get_server(id)

    async def wait_for(self, event: str, *, check: Optional[Callable[..., bool]] = None, timeout: Optional[float] = None) -> Any:
        """Waits for an event

        Parameters
        -----------
        event: :class:`str`
            The name of the event to wait for, without the `on_`
        check: Optional[Callable[..., :class:`bool`]]
            A function that says what event to wait_for, this function takes the same parameters as the event you are waiting for and should return a bool saying if that is the event you want
        timeout: Optional[:class:`float`]
            Time in seconds to wait for the event. By default it waits forever

        Raises
        -------
        asyncio.TimeoutError
            If timeout is provided and it was reached

        Returns
        --------
        Any
            The parameters of the event
        """
        if not check:
            check = lambda *_: True

        future = asyncio.get_running_loop().create_future()
        self.temp_listeners.setdefault(event, []).append((check, future))

        return await asyncio.wait_for(future, timeout)

    def listen(self, name: str | None = None) -> Callable[[Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]]:
        """Registers a listener for an event, multiple listeners can be registered to the same event without conflict

        Parameters
        -----------
        name: Optional[:class:`str`]
            The name of the event to register this under, this defaults to the function's name
        """
        def inner(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]:
            nonlocal name

            if not name:
                if not func.__name__.startswith("on_"):
                    raise RevoltError("listener name must begin with `on_`")

                name = func.__name__[3:]

            self.listeners.setdefault(name, []).append(func)
            return func

        return inner

    @overload
    def remove_listener(self, func: Callable[P, Coroutine[Any, Any, R]], *, event: str = ...) -> Callable[..., Coroutine[Any, Any, R]] | None:
        ...

    @overload
    def remove_listener(self, func: Callable[P, Coroutine[Any, Any, Any]], *, event: None = ...) -> None:
        ...

    def remove_listener(self, func: Callable[P, Coroutine[Any, Any, R]], *, event: str | None = None) -> Callable[..., Coroutine[Any, Any, R]] | None:
        """Removes a listener registered, if the `event` parameter is passed, the listener will only be removed from that event, this can be used if the same listener is registed to multiple events at once.

        Parameters
        -----------
        func: Callable
            The function for the listener to be removed
        event: Optional[:class:`str`]
            The name of the event to remove this from, passing `None` will make this remove the listener from all events this is registered under
        """
        if event is None:
            for listeners in self.listeners.values():
                try:
                    listeners.remove(func)
                except ValueError:
                    pass

        else:
            try:
                self.listeners[event].remove(func)
                return func
            except ValueError:
                pass

    @property
    def user(self) -> User:
        """:class:`User` the user corrasponding to the client"""
        user = self.websocket.user

        assert user
        return user

    @property
    def users(self) -> list[User]:
        """list[:class:`User`] All users the client can see"""
        return list(self.state.users.values())

    @property
    def servers(self) -> list[Server]:
        """list[:class:'Server'] All servers the client can see"""
        return list(self.state.servers.values())

    @property
    def global_emojis(self) -> list[Emoji]:
        return self.state.global_emojis

    async def fetch_user(self, user_id: str) -> User:
        """Fetchs a user

        Parameters
        -----------
        user_id: :class:`str`
            The id of the user you are fetching

        Returns
        --------
        :class:`User`
            The user with the matching id
        """
        payload = await self.http.fetch_user(user_id)
        return User(payload, self.state)

    async def fetch_dm_channels(self) -> list[Union[DMChannel, GroupDMChannel]]:
        """Fetchs all dm channels the client has made

        Returns
        --------
        list[Union[:class:`DMChanel`, :class:`GroupDMChannel`]]
            A list of :class:`DMChannel` or :class`GroupDMChannel`
        """
        channel_payloads = await self.http.fetch_dm_channels()
        return cast(list[Union[DMChannel, GroupDMChannel]], [channel_factory(payload, self.state) for payload in channel_payloads])

    async def fetch_channel(self, channel_id: str) -> Union[DMChannel, GroupDMChannel, SavedMessageChannel, TextChannel, VoiceChannel]:
        """Fetches a channel

        Parameters
        -----------
        channel_id: :class:`str`
            The id of the channel

        Returns
        --------
        Union[:class:`DMChannel`, :class:`GroupDMChannel`, :class:`SavedMessageChannel`, :class:`TextChannel`, :class:`VoiceChannel`]
            The channel with the matching id
        """
        payload = await self.http.fetch_channel(channel_id)

        return channel_factory(payload, self.state)

    async def fetch_server(self, server_id: str) -> Server:
        """Fetchs a server

        Parameters
        -----------
        server_id: :class:`str`
            The id of the server you are fetching

        Returns
        --------
        :class:`Server`
            The server with the matching id
        """
        payload = await self.http.fetch_server(server_id)

        return Server(payload, self.state)

    async def fetch_invite(self, code: str) -> Invite:
        """Fetchs an invite

        Parameters
        -----------
        code: :class:`str`
            The code of the invite you are fetching

        Returns
        --------
        :class:`Invite`
            The invite with the matching code
        """
        payload = await self.http.fetch_invite(code)

        return Invite(payload, code, self.state)

    def get_message(self, message_id: str) -> Message:
        """Gets a message from the cache

        Parameters
        -----------
        message_id: :class:`str`
            The id of the message you are getting

        Returns
        --------
        :class:`Message`
            The message with the matching id

        Raises
        -------
        LookupError
            This raises if the message is not found in the cache
        """
        for message in self.state.messages:
            if message.id == message_id:
                return message

        raise LookupError

    async def edit_self(self, **kwargs: Any) -> None:
        """Edits the client's own user

        Parameters
        -----------
        avatar: Optional[:class:`File`]
            The avatar to change to, passing in ``None`` will remove the avatar
        """
        if kwargs.get("avatar", Missing) is None:
            del kwargs["avatar"]
            remove = ["Avatar"]
        else:
            remove = None

        await self.state.http.edit_self(remove, kwargs)

    async def edit_status(self, **kwargs: Any) -> None:
        """Edits the client's own status

        Parameters
        -----------
        presence: :class:`PresenceType`
            The presence to change to
        text: Optional[:class:`str`]
            The text to change the status to, passing in ``None`` will remove the status
        """
        if kwargs.get("text", Missing) is None:
            del kwargs["text"]
            remove = ["StatusText"]
        else:
            remove = None

        if presence := kwargs.get("presence"):
            kwargs["presence"] = presence.value

        await self.state.http.edit_self(remove, {"status": kwargs})

    async def edit_profile(self, **kwargs: Any) -> None:
        """Edits the client's own profile

        Parameters
        -----------
        content: Optional[:class:`str`]
            The new content for the profile, passing in ``None`` will remove the profile content
        background: Optional[:class:`File`]
            The new background for the profile, passing in ``None`` will remove the profile background
        """
        remove: list[str] = []

        if kwargs.get("content", Missing) is None:
            del kwargs["content"]
            remove.append("ProfileContent")

        if kwargs.get("background", Missing) is None:
            del kwargs["background"]
            remove.append("ProfileBackground")

        await self.state.http.edit_self(remove, {"profile": kwargs})

    async def fetch_emoji(self, emoji_id: str) -> Emoji:
        """Fetches an emoji

        Parameters
        -----------
        emoji_id: str
            The id of the emoji

        Returns
        --------
        :class:`Emoji`
            The emoji with the corrasponding id
        """

        emoji = await self.state.http.fetch_emoji(emoji_id)

        return Emoji(emoji, self.state)

    async def upload_file(self, file: File, tag: Literal['attachments', 'avatars', 'backgrounds', 'icons', 'banners', 'emojis']) -> Ulid:
        """Uploads a file to revolt

        Parameters
        -----------
        file: :class:`File`
            The file to upload
        tag: :class:`str`
            The type of file to upload, this should a string of either `'attachments'`, `'avatars'`, `'backgrounds'`, `'icons'`, `'banners'` or `'emojis'`
        Returns
        --------
        :class:`Ulid`
            The id of the file that was uploaded
        """
        asset = await self.http.upload_file(file, tag)

        ulid = Ulid()
        ulid.id = asset["id"]

        return ulid
