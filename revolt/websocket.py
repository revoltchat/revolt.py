from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Callable, cast

from .types import Message as MessagePayload

try:
    import ujson as json
except ImportError:
    import json

try:
    import msgpack
    use_msgpack = True
except ImportError:
    use_msgpack = False

if TYPE_CHECKING:
    import aiohttp

    from .state import State
    from .types import AuthenticatePayload, BasePayload
    from .types import Member as MemberPayload
    from .types import MessageEventPayload, ReadyEventPayload


__all__ = ("WebsocketHandler",)

logger = logging.getLogger("revolt")

class WebsocketHandler:
    __slots__ = ("session", "token", "ws_url", "dispatch", "state", "websocket", "loop")

    def __init__(self, session: aiohttp.ClientSession, token: str, ws_url: str, dispatch: Callable[..., None], state: State):
        self.session = session
        self.token = token
        self.ws_url = ws_url
        self.dispatch = dispatch
        self.state = state
        self.websocket: aiohttp.ClientWebSocketResponse
        self.loop = asyncio.get_running_loop()

    async def send_payload(self, payload: BasePayload):
        if use_msgpack:
            await self.websocket.send_bytes(msgpack.packb(payload))  # type: ignore
        else:
            await self.websocket.send_str(json.dumps(payload))

    async def heartbeat(self):
        while not self.websocket.closed:
            logger.info("Sending hearbeat")
            await self.websocket.ping()
            await asyncio.sleep(15)

    async def send_authenticate(self):
        payload: AuthenticatePayload = {
            "type": "Authenticate",
            "token": self.token
        }

        await self.send_payload(payload)

    async def handle_event(self, payload: BasePayload):
        event_type = payload["type"].lower()
        logger.debug("Recieved event %s %s", event_type, payload)
        try:
            func = getattr(self, f"handle_{event_type}")
        except:
            logger.debug("Unknown event '%s'", event_type)
            return

        await func(payload)

    async def handle_authenticated(self, _):
        logger.info("Successfully authenticated")

    async def handle_ready(self, payload: ReadyEventPayload):
        for user in payload["users"]:
            self.state.add_user(user)

        for server in payload["servers"]:
            self.state.add_server(server)

        for channel in payload["channels"]:
            self.state.add_channel(channel)

        for member in payload["members"]:
            self.state.add_member(member["_id"]["server"], member)

        await self.state.fetch_all_server_members()

        self.dispatch("ready")

    async def handle_message(self, payload: MessageEventPayload):
        message = self.state.add_message(cast(MessagePayload, payload))
        self.dispatch("message", message)

    async def start(self):
        if use_msgpack:
            url = f"{self.ws_url}?format=msgpack"
        else:
            url = f"{self.ws_url}?format=json"

        self.websocket = await self.session.ws_connect(url)
        await self.send_authenticate()
        asyncio.create_task(self.heartbeat())

        async for msg in self.websocket:
            if use_msgpack:
                payload = msgpack.unpackb(msg.data)
            else:
                payload = json.loads(msg.data)

            self.loop.create_task(self.handle_event(payload))
