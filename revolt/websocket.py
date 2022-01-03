from __future__ import annotations

import asyncio
import logging
from copy import copy
from typing import TYPE_CHECKING, Callable, cast

from .enums import RelationshipType
from .types import (ChannelCreateEventPayload, ChannelDeleteEventPayload,
                    ChannelDeleteTypingEventPayload,
                    ChannelStartTypingEventPayload, ChannelUpdateEventPayload)
from .types import Message as MessagePayload
from .types import (MessageDeleteEventPayload, MessageUpdateEventPayload,
                    ServerDeleteEventPayload, ServerMemberJoinEventPayload,
                    ServerMemberLeaveEventPayload,
                    ServerMemberUpdateEventPayload,
                    ServerRoleDeleteEventPayload, ServerRoleUpdateEventPayload,
                    ServerUpdateEventPayload, UserRelationshipEventPayload,
                    UserUpdateEventPayload)
from .user import Status

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
    __slots__ = ("session", "token", "ws_url", "dispatch", "state", "websocket", "loop", "user", "ready")

    def __init__(self, session: aiohttp.ClientSession, token: str, ws_url: str, dispatch: Callable[..., None], state: State):
        self.session = session
        self.token = token
        self.ws_url = ws_url
        self.dispatch = dispatch
        self.state = state
        self.websocket: aiohttp.ClientWebSocketResponse
        self.loop = asyncio.get_running_loop()
        self.user = None
        self.ready = asyncio.Event()

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
            if event_type != "ready":
                await self.ready.wait()

            func = getattr(self, f"handle_{event_type}")
        except:
            logger.debug("Unknown event '%s'", event_type)
            return

        await func(payload)

    async def handle_authenticated(self, _):
        logger.info("Successfully authenticated")

    async def handle_ready(self, payload: ReadyEventPayload):
        for user_payload in payload["users"]:
            user = self.state.add_user(user_payload)

            if user.relationship == RelationshipType.user:
                self.user = user

        for channel in payload["channels"]:
            self.state.add_channel(channel)

        for server in payload["servers"]:
            self.state.add_server(server)


        for member in payload["members"]:
            self.state.add_member(member["_id"]["server"], member)

        await self.state.fetch_all_server_members()

        self.ready.set()
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

        try:
            message = self.state.get_message(payload["id"])
        except:
            return

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

    async def handle_channelstoptyping(self, payload: ChannelDeleteTypingEventPayload):
        channel = self.state.get_channel(payload["id"])
        user = self.state.get_user(payload["user"])

        self.dispatch("typing_stop", channel, user)

    async def handle_serverupdate(self, payload: ServerUpdateEventPayload):
        server = self.state.get_server(payload["id"])

        old_server = copy(server)

        server._update(**payload["data"])

        if clear := payload.get("clear"):
            if clear == "Icon":
                server.icon = None

            elif clear == "Banner":
                server.banner = None

            elif clear == "Description":
                server.description = None

        self.dispatch("server_update", old_server, server)

    async def handle_serverdelete(self, payload: ServerDeleteEventPayload):
        server = self.state.servers.pop(payload["id"])

        for channel in server.channels:
            del self.state.channels[channel.id]

        self.dispatch("server_delete", server)

    async def handle_servermemberupdate(self, payload: ServerMemberUpdateEventPayload):
        member = self.state.get_member(payload["id"]["server"], payload["id"]["user"])
        old_member = copy(member)

        if clear := payload.get("clear"):
            if clear == "Nickname":
                member.nickname = None
            elif clear == "Avatar":
                member.guild_avatar = None

        member._update(**payload["data"])

        self.dispatch("member_update", old_member, member)

    async def handle_servermemberjoin(self, payload: ServerMemberJoinEventPayload):
        member = self.state.add_member(payload["id"], {"_id": {"server": payload["id"], "user": payload["user"]}})
        self.dispatch("member_join", member)

    async def handle_memberleave(self, payload: ServerMemberLeaveEventPayload):
        server = self.state.get_server(payload["id"])
        member = server._members.pop(payload["user"])

        self.dispatch("member_leave", member)

    async def handle_serveroleupdate(self, payload: ServerRoleUpdateEventPayload):
        server = self.state.get_server(payload["id"])
        role = server.get_role(payload["role_id"])
        old_role = copy(role)

        if clear := payload.get("clear"):
            if clear == "Colour":
                role.colour = None

        role._update(**payload["data"])

        self.dispatch("role_update", old_role, role)

    async def handle_serverroledelete(self, payload: ServerRoleDeleteEventPayload):
        server = self.state.get_server(payload["id"])
        role = server._roles.pop(payload["role_id"])

        self.dispatch("role_delete", role)

    async def handle_userupdate(self, payload: UserUpdateEventPayload):
        user = self.state.get_user(payload["id"])
        old_user = copy(user)

        if clear := payload.get("clear"):
            if clear == "ProfileContent":
                ...
            elif clear == "ProfileBackground":
                ...
            elif clear == "StatusText":
                # user.status will never be none because they are trying to remove the text
                if user.status.presence is None:  # type: ignore
                    user.status = None
                else:
                    user.status = Status(None, user.status.presence)  # type: ignore

            elif clear == "Avatar":
                user.original_avatar = None

        # the keys have . in them so i need to replace with _

        data = payload["data"]
        data["profile_content"] = data.pop("profile.content", None)
        data["profile_background"] = data.pop("profile.background", None)

        user._update(**data)

        self.dispatch("user_update", old_user, user)

    async def handle_userrelationship(self, payload: UserRelationshipEventPayload):
        user = self.state.get_user(payload["user"])
        old_relationship = user.relationship
        user.relationship = RelationshipType(payload["status"])

        self.dispatch("user_relationship_update", user, old_relationship, user.relationship)

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
