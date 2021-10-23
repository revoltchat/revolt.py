from __future__ import annotations

import asyncio
import logging
from copy import copy
from typing import TYPE_CHECKING, Callable, cast

from .types import (ChannelCreateEventPayload, ChannelDeleteEventPayload,
                    ChannelDeleteTypingEventPayload,
                    ChannelStartTypingEventPayload, ChannelUpdateEventPayload)
from .types import Message as MessagePayload
from .types import MessageDeleteEventPayload, MessageUpdateEventPayload

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

        for channel in payload["channels"]:
            self.state.add_channel(channel)

        for server in payload["servers"]:
            self.state.add_server(server)


        for member in payload["members"]:
            self.state.add_member(member["_id"]["server"], member)

        await self.state.fetch_all_server_members()

        self.dispatch("ready")

    async def handle_message(self, payload: MessageEventPayload):
        message = self.state.add_message(cast(MessagePayload, payload))
        self.dispatch("message", message)

    async def handle_messageupdate(self, payload: MessageUpdateEventPayload):
        self.dispatch("raw_message_update", payload)

        message = self.state.get_message(payload["id"])

        data = payload["data"]
        kwargs = {}

        if data["content"]:
            kwargs["content"] = data["content"]

        if data["edited"]["$date"]:
            kwargs["edited_at"] = data["edited"]["$date"]

        message._update(**kwargs)

        self.dispatch("message_update", message)

    async def handle_messagedelete(self, payload: MessageDeleteEventPayload):
        self.dispatch("raw_message_delete", payload)

        message = self.state.get_message(payload["id"])
        if message:
            self.state.messages.remove(message)
            self.dispatch("message_delete", message)

    async def handle_channelcreate(self, payload: ChannelCreateEventPayload):
        channel = self.state.add_channel(payload)

        self.dispatch("channel_create", channel)

    async def handle_channelupdate(self, payload: ChannelUpdateEventPayload):
        channel = self.state.get_channel(payload["id"])

        old_channel = copy(channel)

        channel._update(**payload["data"])

        if clear := payload.get("clear"):
            if clear == "Icon":
                pass  # TODO

            elif clear == "Description":
                channel.description = None  # type: ignore

        self.dispatch("channel_update", old_channel, channel)

    async def handle_channeldelete(self, payload: ChannelDeleteEventPayload):
        channel = self.state.channels.pop(payload["id"])

        self.dispatch("channel_delete", channel)

    async def handle_channelstarttyping(self, payload: ChannelStartTypingEventPayload):
        channel = self.state.get_channel(payload["id"])
        user = self.state.get_user(payload["user"])

        self.dispatch("typing_start", channel, user)

    async def handle_channeldeletetyping(self, payload: ChannelDeleteTypingEventPayload):
        channel = self.state.get_channel(payload["id"])
        user = self.state.get_user(payload["user"])

        self.dispatch("typing_delete", channel, user)

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
