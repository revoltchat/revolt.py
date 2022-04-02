from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict, Union
from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .file import File
    from .message import Message


__all__ = (
    "SavedMessages",
    "DMChannel",
    "GroupDMChannel",
    "TextChannel",
    "VoiceChannel",
    "Channel",
)

class BaseChannel(TypedDict):
    _id: str
    nonce: str

class SavedMessages(BaseChannel):
    user: str
    channel_type: Literal["SavedMessages"]

class DMChannel(BaseChannel):
    active: bool
    recipients: list[str]
    last_message: Message
    channel_type: Literal["DirectMessage"]

class GroupDMChannel(BaseChannel):
    recipients: list[str]
    name: str
    owner: str
    channel_type: Literal["Group"]
    icon: NotRequired[File]
    permissions: NotRequired[int]
    description: NotRequired[str]

class TextChannel(BaseChannel):
    server: str
    name: str
    description: str
    channel_type: Literal["TextChannel"]
    icon: NotRequired[File]
    default_permissions: NotRequired[int]
    role_permissions: NotRequired[dict[str, int]]
    last_message: NotRequired[str]

class VoiceChannel(BaseChannel):
    server: str
    name: str
    description: str
    channel_type: Literal["VoiceChannel"]
    icon: NotRequired[File]
    default_permissions: NotRequired[int]
    role_permissions: NotRequired[dict[str, int]]

Channel = Union[SavedMessages, DMChannel, GroupDMChannel, TextChannel, VoiceChannel]
