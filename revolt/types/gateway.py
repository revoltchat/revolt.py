from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

from .message import Message

if TYPE_CHECKING:
    from .channel import Channel
    from .member import Member
    from .server import Server
    from .user import User


__all__ = (
    "BasePayload",
    "AuthenticatePayload",
    "ReadyEventPayload",
    "MessageEventPayload",
    "MessageUpdateEventPayload",
    "MessageDeleteEventPayload",
)

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

class MessageUpdateData(TypedDict):
    content: str
    edited: dict[str, Any]

class MessageUpdateEventPayload(BasePayload):
    channel: str
    data: MessageUpdateData
    id: str

class MessageDeleteEventPayload(BasePayload):
    channel: str
    id: str
