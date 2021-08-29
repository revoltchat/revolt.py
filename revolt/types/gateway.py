from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from .message import Message

if TYPE_CHECKING:
    from .user import User
    from .server import Server
    from .channel import Channel
    from .member import Member

class BasePayload(TypedDict):
    type: str

class AuthenticatePayload(BasePayload):
    token: str

class ReadyEventPayload(BasePayload):
    users: list[User]
    servers: list[Server]
    channels: list[Channel]
    members: list[Member]

class MessageEventPayload(BasePayload, Message):
    pass
