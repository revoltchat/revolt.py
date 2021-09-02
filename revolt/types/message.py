from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Union

if TYPE_CHECKING:
    from .embed import Embed
    from .file import File


__all__ = ("Message",)

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

class _OptionalMessage(TypedDict):
    attachments: list[File]
    embeds: list[Embed]

class Message(_OptionalMessage):
    _id: str
    channel: str
    author: str
    content: Union[str, UserAddContent, UserRemoveContent, UserJoinedContent, UserLeftContent, UserKickedContent, UserBannedContent, ChannelRenameContent, ChannelDescriptionChangeContent, ChannelIconChangeContent]
