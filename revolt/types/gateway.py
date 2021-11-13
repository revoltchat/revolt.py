from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict, Union

from .channel import (Channel, DMChannel, Group, SavedMessages, TextChannel,
                      VoiceChannel)
from .message import Message

if TYPE_CHECKING:
    from .member import Member, MemberID
    from .server import Server
    from .user import Status, User

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
    "ChannelDeleteTypingEventPayload",
    "ServerUpdateEventPayload",
    "ServerDeleteEventPayload",
    "ServerMemberUpdateEventPayload",
    "ServerMemberJoinEventPayload",
    "ServerMemberLeaveEventPayload",
    "ServerRoleUpdateEventPayload",
    "ServerRoleDeleteEventPayload",
    "UserUpdateEventPayload",
    "UserRelationshipEventPayload"
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
    clear: Literal["Icon", "Description"]

class ChannelDeleteEventPayload(BasePayload):
    id: str

class ChannelStartTypingEventPayload(BasePayload):
    id: str
    user: str

ChannelDeleteTypingEventPayload = ChannelStartTypingEventPayload

class ServerUpdateEventPayload(BasePayload):
    id: str
    data: dict
    clear: Literal["Icon", "Banner", "Description"]

class ServerDeleteEventPayload(BasePayload):
    id: str

class ServerMemberUpdateEventPayload(BasePayload):
    id: MemberID
    data: dict
    clear: Literal["Nickname", "Avatar"]

class ServerMemberJoinEventPayload(BasePayload):
    id: str
    user: str

ServerMemberLeaveEventPayload = ServerMemberJoinEventPayload

class ServerRoleUpdateEventPayload(BasePayload):
    id: str
    role_id: str
    data: dict
    clear: Literal["Color"]

class ServerRoleDeleteEventPayload(BasePayload):
    id: str
    role_id: str

class UserUpdateEventPayload(BasePayload):
    id: str
    data: dict
    clear: Literal["ProfileContent", "ProfileBackground", "StatusText", "Avatar"]

class UserRelationshipEventPayload(BasePayload):
    id: str
    user: str
    status: Status
