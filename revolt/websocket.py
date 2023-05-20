from __future__ import annotations

import asyncio
import logging
import time
from copy import copy
from typing import TYPE_CHECKING, Callable, NamedTuple, cast

from . import utils
from .channel import GroupDMChannel, TextChannel, VoiceChannel
from .enums import RelationshipType
from .role import Role
from .types import (BulkMessageDeleteEventPayload, ChannelCreateEventPayload,
                    ChannelDeleteEventPayload, ChannelDeleteTypingEventPayload,
                    ChannelStartTypingEventPayload, ChannelUpdateEventPayload)
from .types import Member as MemberPayload
from .types import MemberID as MemberIDPayload
from .types import Message as MessagePayload
from .types import (MessageDeleteEventPayload, MessageReactEventPayload,
                    MessageRemoveReactionEventPayload,
                    MessageUnreactEventPayload, MessageUpdateEventPayload)
from .types import Role as RolePayload
from .types import (ServerCreateEventPayload, ServerDeleteEventPayload,
                    ServerMemberJoinEventPayload,
                    ServerMemberLeaveEventPayload,
                    ServerMemberUpdateEventPayload,
                    ServerRoleDeleteEventPayload, ServerRoleUpdateEventPayload,
                    ServerUpdateEventPayload, UserRelationshipEventPayload,
                    UserUpdateEventPayload)
from .user import Status, User, UserProfile

import aiohttp

try:
    import ujson as json
except ImportError:
    import json

use_msgpack: bool

try:
    import msgpack
    use_msgpack = True
except ImportError:
    use_msgpack = False

if TYPE_CHECKING:
    import aiohttp

    from .state import State
    from .types import (AuthenticatePayload, BasePayload, MessageEventPayload,
                        ReadyEventPayload)
    from .message import Message

class WSMessage(NamedTuple):
    type: aiohttp.WSMsgType
    data: str | bytes | aiohttp.WSCloseCode

__all__: tuple[str, ...] = ("WebsocketHandler",)

logger: logging.Logger = logging.getLogger("revolt")

class WebsocketHandler:
    __slots__ = ("session", "token", "ws_url", "dispatch", "state", "websocket", "loop", "user", "ready", "server_events")

    def __init__(self, session: aiohttp.ClientSession, token: str, ws_url: str, dispatch: Callable[..., None], state: State):
        self.session: aiohttp.ClientSession = session
        self.token: str = token
        self.ws_url: str = ws_url
        self.dispatch: Callable[..., None] = dispatch
        self.state: State = state
        self.websocket: aiohttp.ClientWebSocketResponse
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self.user: User | None = None
        self.ready: asyncio.Event = asyncio.Event()
        self.server_events: dict[str, asyncio.Event] = {}

    async def _wait_for_server_ready(self, server_id: str) -> None:
        if event := self.server_events.get(server_id):
            await event.wait()

    async def send_payload(self, payload: BasePayload) -> None:
        if use_msgpack:
            await self.websocket.send_bytes(msgpack.packb(payload))
        else:
            await self.websocket.send_str(json.dumps(payload))

    async def heartbeat(self) -> None:
        while not self.websocket.closed:
            logger.info("Sending hearbeat")
            await self.websocket.ping()
            await asyncio.sleep(15)

    async def send_authenticate(self) -> None:
        payload: AuthenticatePayload = {
            "type": "Authenticate",
            "token": self.token
        }

        await self.send_payload(payload)

    async def handle_event(self, payload: BasePayload) -> None:
        event_type = payload["type"].lower()
        logger.debug("Recieved event %s %s", event_type, payload)
        try:
            if event_type != "ready":
                await self.ready.wait()

            func = getattr(self, f"handle_{event_type}")
        except AttributeError:
            return logger.debug("Unknown event '%s'", event_type)

        await func(payload)

    async def handle_authenticated(self, _: BasePayload) -> None:
        logger.info("Successfully authenticated")

    async def handle_ready(self, payload: ReadyEventPayload) -> None:
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

        for emoji in payload["emojis"]:
            emoji = self.state.add_emoji(emoji)

        await self.state.fetch_all_server_members()

        self.ready.set()
        self.dispatch("ready")

    async def handle_message(self, payload: MessageEventPayload) -> None:
        if server := self.state.get_channel(payload["channel"]).server_id:
            await self._wait_for_server_ready(server)

        message = self.state.add_message(cast(MessagePayload, payload))


        self.dispatch("message", message)

    async def handle_messageupdate(self, payload: MessageUpdateEventPayload) -> None:
        self.dispatch("raw_message_update", payload)

        try:
            message = self.state.get_message(payload["id"])
        except LookupError:
            return

        if server_id := message.channel.server_id:
            await self._wait_for_server_ready(server_id)

        message._update(**payload["data"])

        self.dispatch("message_update", message)

    async def handle_messagedelete(self, payload: MessageDeleteEventPayload) -> None:
        self.dispatch("raw_message_delete", payload)

        try:
            message = self.state.get_message(payload["id"])
        except LookupError:
            return

        if server_id := message.channel.server_id:
            await self._wait_for_server_ready(server_id)

        self.state.messages.remove(message)


        self.dispatch("message_delete", message)

    async def handle_channelcreate(self, payload: ChannelCreateEventPayload) -> None:
        channel = self.state.add_channel(payload)

        if server_id := channel.server_id:
            await self._wait_for_server_ready(server_id)

        self.dispatch("channel_create", channel)

    async def handle_channelupdate(self, payload: ChannelUpdateEventPayload) -> None:
        # Revolt sends channel updates for channels we dont have permissions to see, a bug, but still can cause issues as its not in the cache

        if not (channel := self.state.channels.get(payload["id"], None)):
            return

        if server_id := channel.server_id:
            await self._wait_for_server_ready(server_id)

        old_channel = copy(channel)

        channel._update(**payload["data"])

        if clear := payload.get("clear"):
            if clear == "Icon":
                if isinstance(channel, (TextChannel, VoiceChannel, GroupDMChannel)):
                    channel.icon = None

            elif clear == "Description":
                if isinstance(channel, (TextChannel, VoiceChannel, GroupDMChannel)):
                    channel.description = None


        self.dispatch("channel_update", old_channel, channel)

    async def handle_channeldelete(self, payload: ChannelDeleteEventPayload) -> None:
        channel = self.state.channels.pop(payload["id"])

        if server_id := channel.server_id:
            await self._wait_for_server_ready(server_id)

        self.dispatch("channel_delete", channel)

    async def handle_channelstarttyping(self, payload: ChannelStartTypingEventPayload) -> None:
        channel = self.state.get_channel(payload["id"])

        if server_id := channel.server_id:
            await self._wait_for_server_ready(server_id)

        user = self.state.get_user(payload["user"])

        self.dispatch("typing_start", channel, user)

    async def handle_channelstoptyping(self, payload: ChannelDeleteTypingEventPayload) -> None:
        channel = self.state.get_channel(payload["id"])

        if server_id := channel.server_id:
            await self._wait_for_server_ready(server_id)

        user = self.state.get_user(payload["user"])

        self.dispatch("typing_stop", channel, user)

    async def handle_serverupdate(self, payload: ServerUpdateEventPayload) -> None:
        await self._wait_for_server_ready(payload["id"])

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

    async def handle_serverdelete(self, payload: ServerDeleteEventPayload) -> None:
        server = self.state.servers.pop(payload["id"])

        for channel in server.channels:
            del self.state.channels[channel.id]

        await self._wait_for_server_ready(server.id)

        self.dispatch("server_delete", server)

    async def handle_servercreate(self, payload: ServerCreateEventPayload) -> None:
        for channel in payload["channels"]:
            self.state.add_channel(channel)

        server = self.state.add_server(payload["server"])

        # lock all server events until we fetch all the members, otherwise the cache will be incomplete
        self.server_events[server.id] = asyncio.Event()
        await self.state.fetch_server_members(server.id)
        self.server_events.pop(server.id).set()

        self.dispatch("server_join", server)

    async def handle_servermemberupdate(self, payload: ServerMemberUpdateEventPayload) -> None:
        await self._wait_for_server_ready(payload["id"]["server"])

        member = self.state.get_member(payload["id"]["server"], payload["id"]["user"])
        old_member = copy(member)

        if clear := payload.get("clear"):
            if clear == "Nickname":
                member.nickname = None
            elif clear == "Avatar":
                member.guild_avatar = None

        member._update(**payload["data"])

        self.dispatch("member_update", old_member, member)

    async def handle_servermemberjoin(self, payload: ServerMemberJoinEventPayload) -> None:
        # avoid an api request if possible
        if payload["user"] not in self.state.users:
            user = await self.state.http.fetch_user(payload["user"])
            self.state.add_user(user)

        member = self.state.add_member(payload["id"], MemberPayload(_id=MemberIDPayload(server=payload["id"], user=payload["user"]), joined_at=int(time.time())))  # revolt doesnt give us the joined at time

        self.dispatch("member_join", member)

    async def handle_memberleave(self, payload: ServerMemberLeaveEventPayload) -> None:
        await self._wait_for_server_ready(payload["id"])

        server = self.state.get_server(payload["id"])
        member = server._members.pop(payload["user"])

        # remove the member from the user

        user = self.state.get_user(payload["user"])
        user._members.pop(server.id)

        self.dispatch("member_leave", member)

    async def handle_serverroleupdate(self, payload: ServerRoleUpdateEventPayload) -> None:
        server = self.state.get_server(payload["id"])
        await self._wait_for_server_ready(server.id)

        try:
            role = server.get_role(payload["role_id"])
        except LookupError:
            # the role wasnt found meaning it was just created

            role = Role(cast(RolePayload, payload["data"]), payload["role_id"], server, self.state)
            server._roles[role.id] = role
            self.dispatch("role_create", role)
        else:
            old_role = copy(role)

            if clear := payload.get("clear"):
                if clear == "Colour":
                    role.colour = None

            role._update(**payload["data"])

            self.dispatch("role_update", old_role, role)

    async def handle_serverroledelete(self, payload: ServerRoleDeleteEventPayload) -> None:
        server = self.state.get_server(payload["id"])
        role = server._roles.pop(payload["role_id"])

        await self._wait_for_server_ready(server.id)

        self.dispatch("role_delete", role)

    async def handle_userupdate(self, payload: UserUpdateEventPayload) -> None:
        user = self.state.get_user(payload["id"])
        old_user = copy(user)

        if clear := payload.get("clear"):
            if clear == "ProfileContent":
                if profile := user.profile:
                    user.profile = UserProfile(None, profile.background)

            elif clear == "ProfileBackground":
                if profile := user.profile:
                    user.profile = UserProfile(profile.content, None)

            elif clear == "StatusText":
                user.status = Status(None, user.status.presence if user.status else None)

            elif clear == "Avatar":
                user.original_avatar = None

        user._update(**payload["data"])

        self.dispatch("user_update", old_user, user)

    async def handle_userrelationship(self, payload: UserRelationshipEventPayload) -> None:
        user = self.state.get_user(payload["user"])
        old_relationship = user.relationship
        user.relationship = RelationshipType(payload["status"])

        self.dispatch("user_relationship_update", user, old_relationship, user.relationship)

    async def handle_messagereact(self, payload: MessageReactEventPayload) -> None:
        if server := self.state.get_channel(payload["channel_id"]).server_id:
            await self._wait_for_server_ready(server)

        self.dispatch("raw_reaction_add", payload["channel_id"], payload["id"], payload["user_id"], payload["emoji_id"])

        try:
            message = utils.get(self.state.messages, id=payload["id"])
        except LookupError:
            return

        user = self.state.get_user(payload["user_id"])
        message.reactions.setdefault(payload["emoji_id"], []).append(user)
        emoji_id = payload["emoji_id"]

        self.dispatch("reaction_add", message, user, emoji_id)

    async def handle_messageunreact(self, payload: MessageUnreactEventPayload) -> None:
        if server := self.state.get_channel(payload["channel_id"]).server_id:
            await self._wait_for_server_ready(server)

        self.dispatch("raw_reaction_remove", payload["channel_id"], payload["id"], payload["user_id"], payload["emoji_id"])

        try:
            message = utils.get(self.state.messages, id=payload["id"])
        except LookupError:
            return

        user = self.state.get_user(payload["user_id"])
        message.reactions[payload["emoji_id"]].remove(user)

        self.dispatch("reaction_remove", message, user, payload["emoji_id"])

    async def handle_messageremovereaction(self, payload: MessageRemoveReactionEventPayload) -> None:
        if server := self.state.get_channel(payload["channel_id"]).server_id:
            await self._wait_for_server_ready(server)

        self.dispatch("raw_reaction_clear", payload["channel_id"], payload["id"], payload["emoji_id"])

        try:
            message = utils.get(self.state.messages, id=payload["id"])
        except LookupError:
            return

        users = message.reactions.pop(payload["emoji_id"])

        self.dispatch("reaction_clear", message, users, payload["emoji_id"])

    async def handle_bulkmessagedelete(self, payload: BulkMessageDeleteEventPayload) -> None:
        channel = self.state.get_channel(payload["channel"])

        self.dispatch("raw_bulk_message_delete", payload)

        messages: list[Message] = []

        for message_id in payload["ids"]:
            if server_id := channel.server_id:
                await self._wait_for_server_ready(server_id)

            self.dispatch("raw_message_delete", MessageDeleteEventPayload(type="messagedelete", channel=payload["channel"], id=message_id))

            try:
                message = self.state.get_message(message_id)
            except LookupError:
                pass
            else:
                self.state.messages.remove(message)
                self.dispatch("message_delete", message)

                messages.append(message)

            self.dispatch("bulk_message_delete", messages)

    async def start(self) -> None:
        if use_msgpack:
            url = f"{self.ws_url}?format=msgpack"
        else:
            url = f"{self.ws_url}?format=json"

        self.websocket = await self.session.ws_connect(url)  # type: ignore
        await self.send_authenticate()
        asyncio.create_task(self.heartbeat())

        async for msg in self.websocket:
            msg = cast(WSMessage, msg)  # aiohttp doesnt use NamedTuple so the type info is missing

            if use_msgpack:
                data = cast(bytes, msg.data)

                payload = msgpack.unpackb(data)
            else:
                data = cast(str, msg.data)

                payload = json.loads(data)

            self.loop.create_task(self.handle_event(payload))
