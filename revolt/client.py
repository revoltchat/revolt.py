from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional, TypeVar

import aiohttp

from .http import HttpClient
from .state import State
from .websocket import WebsocketHandler

try:
    import ujson as json
except ImportError:
    import json

if TYPE_CHECKING:
    from .channel import Channel
    from .server import Server
    from .types import ApiInfo
    from .user import User


__all__ = ("Client",)

logger = logging.getLogger("revolt")

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
    
    def __init__(self, session: aiohttp.ClientSession, token: str, api_url: str = "https://api.revolt.chat", max_messages: int = 5000):
        self.session = session
        self.token = token
        self.api_url = api_url
        self.max_messages = max_messages
        
        self.api_info: ApiInfo
        self.http: HttpClient
        self.state: State
        self.websocket: WebsocketHandler

        self.listeners: dict[str, list[tuple[Callable[..., bool], asyncio.Future[Any]]]] = {}

        super().__init__()

    def dispatch(self, event: str, *args: Any):
        """Dispatch an event, this is typically used for testing and internals.
        
        Parameters
        ----------
        event: class:`str`
            The name of the event to dispatch, not including `on_`
        args: :class:`Any`
            The arguments passed to the event
        """
        for check, future in self.listeners.pop(event, []):
            if check(*args):
                if len(args) == 1:
                    future.set_result(args[0])
                else:
                    future.set_result(args)

        func = getattr(self, f"on_{event}", None)
        if func:
            asyncio.create_task(func(*args))

    async def get_api_info(self) -> ApiInfo:
        async with self.session.get(self.api_url) as resp:
            return json.loads(await resp.text())

    async def start(self):
        """Starts the client"""
        api_info = await self.get_api_info()

        self.api_info = api_info
        self.http = HttpClient(self.session, self.token, self.api_url, self.api_info)
        self.state = State(self.http, api_info, self.max_messages)
        self.websocket = WebsocketHandler(self.session, self.token, api_info["ws"], self.dispatch, self.state)
        await self.websocket.start()

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
        self.listeners.setdefault(event, []).append((check, future))

        return await asyncio.wait_for(future, timeout)

    @property
    def user(self) -> User:
        user = self.websocket.user

        assert user
        return user

    @property
    def users(self) -> list[User]:
        return list(self.state.users.values())
