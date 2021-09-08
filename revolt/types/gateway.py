from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

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
    "MessageUpdateEditedData",
    "MessageUpdateData",
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

MessageUpdateEditedData = TypedDict("MessageUpdateEditedData", {"$date": str})

class MessageUpdateData(TypedDict):
    content: str
    edited: MessageUpdateEditedData

class MessageUpdateEventPayload(BasePayload):
    channel: str
    data: MessageUpdateData
    id: str

class MessageDeleteEventPayload(BasePayload):
    channel: str
    id: str
