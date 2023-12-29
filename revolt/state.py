from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from .channel import Channel, channel_factory
from .emoji import Emoji
from .member import Member
from .message import Message
from .server import Server
from .user import User

if TYPE_CHECKING:
    from .http import HttpClient
    from .types import ApiInfo
    from .types import Channel as ChannelPayload
    from .types import Emoji as EmojiPayload
    from .types import Member as MemberPayload
    from .types import Message as MessagePayload
    from .types import Server as ServerPayload
    from .types import User as UserPayload

__all__ = ("State",)

class State:
    __slots__ = ("http", "api_info", "max_messages", "users", "channels", "servers", "messages", "global_emojis", "user_id", "me")

    def __init__(self, http: HttpClient, api_info: ApiInfo, max_messages: int):
        self.http: HttpClient = http
        self.api_info: ApiInfo = api_info
        self.max_messages: int = max_messages

        self.me: User

        self.users: dict[str, User] = {}
        self.channels: dict[str, Channel] = {}
        self.servers: dict[str, Server] = {}
        self.messages: deque[Message] = deque()
        self.global_emojis: list[Emoji] = []

    def get_user(self, id: str) -> User:
        try:
            return self.users[id]
        except KeyError:
            raise LookupError from None

    def get_member(self, server_id: str, member_id: str) -> Member:
        server = self.servers[server_id]
        return server.get_member(member_id)

    def get_channel(self, id: str) -> Channel:
        try:
            return self.channels[id]
        except KeyError:
            raise LookupError from None

    def get_server(self, id: str) -> Server:
        try:
            return self.servers[id]
        except KeyError:
            raise LookupError from None

    def add_user(self, payload: UserPayload) -> User:


        user = User(payload, self)

        if payload.get("relationship") == "User":
            self.me = user

        self.users[user.id] = user
        return user

    def add_member(self, server_id: str, payload: MemberPayload) -> Member:
        server = self.get_server(server_id)

        return server._add_member(payload)

    def add_channel(self, payload: ChannelPayload) -> Channel:
        channel = channel_factory(payload, self)
        self.channels[channel.id] = channel
        return channel

    def add_server(self, payload: ServerPayload) -> Server:
        server = Server(payload, self)
        self.servers[server.id] = server
        return server

    def add_message(self, payload: MessagePayload) -> Message:
        message = Message(payload, self)
        if len(self.messages) >= self.max_messages:
            self.messages.pop()

        self.messages.appendleft(message)
        return message

    def add_emoji(self, payload: EmojiPayload) -> Emoji:
        emoji = Emoji(payload, self)

        if server_id := emoji.server_id:
            server = self.get_server(server_id)
            server._emojis[emoji.id] = emoji
        else:
            self.global_emojis.append(emoji)

        return emoji

    def get_message(self, message_id: str) -> Message:
        for msg in self.messages:
            if msg.id == message_id:
                return msg

        raise LookupError

    async def fetch_server_members(self, server_id: str) -> None:
        data = await self.http.fetch_members(server_id)

        for user in data["users"]:
            self.add_user(user)

        for member in data["members"]:
            self.add_member(server_id, member)

    async def fetch_all_server_members(self) -> None:
        for server_id in self.servers:
            await self.fetch_server_members(server_id)
