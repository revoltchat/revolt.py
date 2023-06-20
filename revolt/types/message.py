from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Union

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .embed import Embed
    from .file import File


__all__ = (
    "UserAddContent",
    "UserRemoveContent",
    "UserJoinedContent",
    "UserLeftContent",
    "UserKickedContent",
    "UserBannedContent",
    "ChannelRenameContent",
    "ChannelDescriptionChangeContent",
    "ChannelIconChangeContent",
    "Masquerade",
    "Interactions",
    "Message",
    "MessageReplyPayload",
    "SystemMessageContent",
    )

class UserAddContent(TypedDict):
    id: str
    by: str

class UserRemoveContent(TypedDict):
    id: str
    by: str

class UserJoinedContent(TypedDict):
    id: str
    by: str

class UserLeftContent(TypedDict):
    id: str

class UserKickedContent(TypedDict):
    id: str

class UserBannedContent(TypedDict):
    id: str

class ChannelRenameContent(TypedDict):
    name: str
    by: str

class ChannelDescriptionChangeContent(TypedDict):
    by: str

class ChannelIconChangeContent(TypedDict):
    by: str

class Masquerade(TypedDict, total=False):
    name: str
    avatar: str
    colour: str

class Interactions(TypedDict):
    reactions: NotRequired[list[str]]
    restrict_reactions: NotRequired[bool]

SystemMessageContent = Union[UserAddContent, UserRemoveContent, UserJoinedContent, UserLeftContent, UserKickedContent, UserBannedContent, ChannelRenameContent, ChannelDescriptionChangeContent, ChannelIconChangeContent]

class Message(TypedDict):
    _id: str
    channel: str
    author: str
    content: str
    system: NotRequired[SystemMessageContent]
    attachments: NotRequired[list[File]]
    embeds: NotRequired[list[Embed]]
    mentions: NotRequired[list[str]]
    replies: NotRequired[list[str]]
    edited: NotRequired[str | int]
    masquerade: NotRequired[Masquerade]
    interactions: NotRequired[Interactions]
    reactions: dict[str, list[str]]

class MessageReplyPayload(TypedDict):
    id: str
    mention: bool
