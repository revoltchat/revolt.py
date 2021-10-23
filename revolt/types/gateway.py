from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Union

from .channel import (Channel, DMChannel, Group, SavedMessages, TextChannel,
                      VoiceChannel)
from .message import Message

if TYPE_CHECKING:
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
    "ChannelCreateEventPayload",
    "ChannelUpdateEventPayload",
    "ChannelDeleteEventPayload",
    "ChannelStartTypingEventPayload",
    "ChannelDeleteTypingEventPayload"
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

class ChannelCreateEventPayload_SavedMessages(BasePayload, SavedMessages):
    pass

class ChannelCreateEventPayload_Group(BasePayload, Group):
    pass

class ChannelCreateEventPayload_TextChannel(BasePayload, TextChannel):
    pass

class ChannelCreateEventPayload_VoiceChannel(BasePayload, VoiceChannel):
    pass

class ChannelCreateEventPayload_DMChannel(BasePayload, DMChannel):
    pass

ChannelCreateEventPayload = Union[ChannelCreateEventPayload_Group, ChannelCreateEventPayload_Group, ChannelCreateEventPayload_TextChannel, ChannelCreateEventPayload_VoiceChannel, ChannelCreateEventPayload_DMChannel]

class ChannelUpdateEventPayload(BasePayload):
    id: str
    data: ...
    clear: ...

class ChannelDeleteEventPayload(BasePayload):
    id: str

class ChannelStartTypingEventPayload(BasePayload):
    id: str
    user: str

ChannelDeleteTypingEventPayload = ChannelStartTypingEventPayload
