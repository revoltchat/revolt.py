from __future__ import annotations

import asyncio
import aiohttp
from typing import Any, Callable, TypeVar, Coroutine, TYPE_CHECKING, Optional
import logging

from .http import HttpClient
from .state import State
from .websocket import WebsocketHandler

try:
    import ujson as json
except ImportError:
    import json

if TYPE_CHECKING:
    from .payloads import ApiInfo
    from .user import User
    from .server import Server
    from .channel import Channel

logger = logging.getLogger("revolt")

R = TypeVar("R")
Coro = Coroutine[Any, Any, R]

class Client:
    def __init__(self, session: aiohttp.ClientSession, token: str, api_url: str = "https://api.revolt.chat"):
        self.session = session
        self.token = token
        self.api_url = api_url
        self.events: dict[str, list[Callable[..., Coro[None]]]] = {}
        
        self.api_info: ApiInfo
        self.http: HttpClient
        self.state: State
        self.websocket: WebsocketHandler

    def event(self, name: str = None):
        def inner(func: Callable[..., Coro[None]]):
            event_name = name or func.__name__
            self.events.setdefault(event_name, []).append(func)

            return func
        return inner

    def dispatch(self, event: str, *args: Any):
        ...

    async def start(self):
        async with self.session.get(self.api_url) as resp:
            api_info: ApiInfo = json.loads(await resp.text())

        self.api_info = api_info
        self.http = HttpClient(self.session, self.token, self.api_url, self.api_info)
        self.state = State(self.http, api_info)
        self.websocket = WebsocketHandler(self.session, self.token, api_info["ws"], self.dispatch, self.state)
        
        await self.websocket.start()

    def get_user(self, id: str) -> Optional[User]:
        self.state.get_user(id)

    def get_channel(self, id: str) -> Optional[Channel]:
        self.state.get_channel(id)

    def get_server(self, id: str) -> Optional[Server]:
        self.state.get_server(id)
