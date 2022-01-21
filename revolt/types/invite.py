from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .file import File

__all__ = ("Invite", "PartialInvite")


class Invite(TypedDict):
    type: Literal["Server"]
    server_id: str
    server_name: str
    server_icon: NotRequired[str]
    server_banner: NotRequired[str]
    channel_id: str
    channel_name: str
    channel_description: NotRequired[str]
    user_name: str
    user_avatar: NotRequired[File]
    member_count: int

class PartialInvite(TypedDict):
    _id: str
    server: str
    channel: str
    creator: str
