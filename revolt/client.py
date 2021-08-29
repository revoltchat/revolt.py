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
    from .types import ApiInfo
    from .user import User
    from .server import Server
    from .channel import Channel

logger = logging.getLogger("revolt")

class Client:
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

    def dispatch(self, event: str, *args: Any):
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
        api_info = await self.get_api_info()

        self.api_info = api_info
        self.http = HttpClient(self.session, self.token, self.api_url, self.api_info)
        self.state = State(self.http, api_info, self.max_messages)
        self.websocket = WebsocketHandler(self.session, self.token, api_info["ws"], self.dispatch, self.state)
        await self.websocket.start()

    def get_user(self, id: str) -> Optional[User]:
        self.state.get_user(id)

    def get_channel(self, id: str) -> Optional[Channel]:
        self.state.get_channel(id)

    def get_server(self, id: str) -> Optional[Server]:
        self.state.get_server(id)

    def wait_for(self, event: str, *, check: Optional[Callable[..., bool]] = None) -> asyncio.Future[Any]:
        if not check:
            check = lambda *_: True

        future = asyncio.get_running_loop().create_future()
        self.listeners.setdefault(event, []).append((check, future))

        return future