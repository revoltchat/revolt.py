from __future__ import annotations

from typing import Callable, TYPE_CHECKING, cast
import logging
import asyncio

from .payloads import Message as MessagePayload

try:
    import ujson as json
except ImportError:
    import json

if TYPE_CHECKING:
    import aiohttp
    from .payloads import BasePayload, AuthenticatePayload, ReadyEventPayload, MessageEventPayload, Member as MemberPayload
    from .state import State

logger = logging.getLogger("revolt")

class WebsocketHandler:
    def __init__(self, session: aiohttp.ClientSession, token: str, ws_url: str, dispatch: Callable[..., None], state: State):
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
            server_id = member["_id"]["server"]
            member_payload: MemberPayload = member | {"_id": member["_id"]["user"]}  # type: ignore
            self.state.add_member(server_id, member_payload)

        self.dispatch("ready")

    async def handle_message(self, payload: MessageEventPayload):
        message = self.state.add_message(cast(MessagePayload, payload))
        self.dispatch("message", message)

    async def start(self):
        self.websocket = await self.session.ws_connect(self.ws_url)

        await self.send_authenticate()
        asyncio.create_task(self.heartbeat())

        async for msg in self.websocket:
            await self.handle_event(json.loads(msg.data))
