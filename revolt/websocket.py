from __future__ import annotations

from typing import Callable, TYPE_CHECKING
import logging
import asyncio

try:
    import ujson as json
except ImportError:
    import json

if TYPE_CHECKING:
    import aiohttp
    from .payloads import BasePayload, AuthenticatePayload, ReadyPayload
    from .state import State

logger = logging.getLogger("revolt")

class WebsocketHandler:
    def __init__(self, session: aiohttp.ClientSession, token: str, ws_url: str, dispatch: Callable, state: State):
        self.session = session
        self.token = token
        self.ws_url = ws_url
        self.dispatch = dispatch
        self.state = state
        self.websocket: aiohttp.ClientWebSocketResponse

    async def send_payload(self, payload: BasePayload):
        await self.websocket.send_str(json.dumps(payload))

    async def heartbeat(self):
        while not self.websocket.closed:
            await self.send_payload({"type": "Ping"})
            await asyncio.sleep(15)

    async def send_authenticate(self):
        payload: AuthenticatePayload = {
            "type": "Authenticate",
            "token": self.token
        }

        await self.send_payload(payload)

    async def handle_event(self, payload: BasePayload):
        event_type = payload["type"].lower()
        print(event_type)
        try:
            func = getattr(self, f"handle_{event_type}")
        except:
            logger.debug("Unknown event '%s'", event_type)
            return

        await func(payload)

    async def handle_ready(self, payload: ReadyPayload):
        for user in payload["users"]:
            self.state.add_user(user)
        
        for server in payload["servers"]:
            self.state.add_server(server)

        for channel in payload["channels"]:
            self.state.add_channel(channel)

    async def start(self):
        self.websocket = await self.session.ws_connect(self.ws_url)

        await self.send_authenticate()
        asyncio.create_task(self.heartbeat())

        async for msg in self.websocket:
            await self.handle_event(json.loads(msg.data))
