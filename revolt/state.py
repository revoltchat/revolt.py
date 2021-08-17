from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .user import User
from .channel import Channel, channel_factory
from .server import Server

if TYPE_CHECKING:
    from .http import HttpClient
    from .payloads import ApiInfo, User as UserPayload, Channel as ChannelPayload, Server as ServerPayload

class State:
    def __init__(self, http: HttpClient, api_info: ApiInfo):
        self.http = http
        self.api_info = api_info

        self.users: dict[str, User] = {}
        self.channels: dict[str, Channel] = {}
        self.servers: dict[str, Server] = {}

    def get_user(self, id: str) -> Optional[User]:
        self.users.get(id)

    def get_channel(self, id: str) -> Optional[Channel]:
        self.channels.get(id)

    def get_server(self, id: str) -> Optional[Server]:
        self.channels.get(id)

    def add_user(self, payload: UserPayload) -> User:
        user = User(payload, self)
        self.users[user.id] = user
        return user

    def add_channel(self, payload: ChannelPayload) -> Channel:
        cls = channel_factory(payload)
        channel = cls(payload, self)
        self.channels[channel.id] = channel
        return channel

    def add_server(self, payload: ServerPayload) -> Server:
        server = Server(payload, self)
        self.servers[server.id] = server
        return server
