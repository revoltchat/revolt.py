from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, Optional

from .channel import Channel, channel_factory
from .member import Member
from .message import Message
from .server import Server
from .user import User

if TYPE_CHECKING:
    from .http import HttpClient
    from .types import ApiInfo
    from .types import Channel as ChannelPayload
    from .types import Member as MemberPayload
    from .types import Message as MessagePayload
    from .types import Server as ServerPayload
    from .types import User as UserPayload


__all__ = ("State",)

class State:
    __slots__ = ("http", "api_info", "max_messages", "users", "channels", "servers", "messages")

    def __init__(self, http: HttpClient, api_info: ApiInfo, max_messages: int):
        self.http = http
        self.api_info = api_info
        self.max_messages = max_messages

        self.users: dict[str, User] = {}
        self.channels: dict[str, Channel] = {}
        self.servers: dict[str, Server] = {}
        self.messages: deque[Message] = deque()

    def get_user(self, id: str) -> Optional[User]:
        return self.users.get(id)

    def get_member(self, server_id: str, member_id: str) -> Optional[Member]:
        server = self.servers.get(server_id)
        
        if server:
            return server.get_member(member_id)

    def get_channel(self, id: str) -> Optional[Channel]:
        return self.channels.get(id)

    def get_server(self, id: str) -> Optional[Server]:
        return self.servers.get(id)

    def add_user(self, payload: UserPayload) -> User:
        user = User(payload, self)
        self.users[user.id] = user
        return user

    def add_member(self, server_id: str, payload: MemberPayload) -> Optional[Member]:
        server = self.get_server(server_id)

        if not server:
            return

        member = Member(payload, server, self)

        server._members[member.id] = member
        return member

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

    def get_message(self, message_id: str) -> Optional[Message]:
        for msg in self.messages:
            if msg.id == message_id:
                return msg

    async def fetch_all_server_members(self):
        for server_id in self.servers.keys():
            data = await self.http.fetch_members(server_id)
            
            for user in data["users"]:
                self.add_user(user)
            
            for member in data["members"]:
                self.add_member(server_id, member)
