from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict, Union

if TYPE_CHECKING:
    from .file import File
    from .message import Message


__all__ = (
    "SavedMessages",
    "DMChannel",
    "Group",
    "TextChannel",
    "VoiceChannel",
    "Channel",
)

class _NonceChannel(TypedDict, total=False):
    nonce: str

class BaseChannel(TypedDict):
    _id: str

class SavedMessages(_NonceChannel, BaseChannel):
    user: str
    channel_type: Literal["SavedMessage"]

class DMChannel(_NonceChannel, BaseChannel):
    active: bool
    recipients: list[str]
    last_message: Message
    channel_type: Literal["DirectMessage"]

class _GroupOptional(TypedDict):
    icon: File
    permissions: int
    description: str

class Group(_NonceChannel, _GroupOptional, BaseChannel):
    recipients: list[str]
    name: str
    owner: str
    channel_type: Literal["Group"]

class _TextChannelOptional(TypedDict, total=False):
    icon: File
    default_permissions: int
    role_permissions: dict[str, int]

class TextChannel(_NonceChannel, _TextChannelOptional, BaseChannel):
    server: str
    name: str
    description: str
    last_message: str
    channel_type: Literal["TextChannel"]

class _VoiceChannelOptional(TypedDict, total=False):
    icon: File
    default_permissions: int
    role_permissions: int

class VoiceChannel(_NonceChannel, _TextChannelOptional, BaseChannel):
    server: str
    name: str
    description: str
    channel_type: Literal["VoiceChannel"]

Channel = Union[SavedMessages, DMChannel, Group, TextChannel, VoiceChannel]
