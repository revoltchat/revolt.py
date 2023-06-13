from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .file import File

__all__ = (
    "UserRelation",
    "Relation",
    "UserBot",
    "Status",
    "User",
    "UserProfile",
)

Relation = Literal["Blocked", "BlockedOther", "Friend", "Incoming", "None", "Outgoing", "User"]

class UserBot(TypedDict):
    owner: str

class Status(TypedDict, total=False):
    text: str
    presence: Literal["Busy", "Idle", "Invisible", "Online"]

class UserRelation(TypedDict):
    status: Relation
    _id: str

class User(TypedDict):
    _id: str
    username: str
    discriminator: str
    display_name: NotRequired[str]
    avatar: NotRequired[File]
    relations: NotRequired[list[UserRelation]]
    badges: NotRequired[int]
    status: NotRequired[Status]
    relationship: NotRequired[Relation]
    online: NotRequired[bool]
    flags: NotRequired[int]
    bot: NotRequired[UserBot]
    privileged: NotRequired[bool]

class UserProfile(TypedDict, total=False):
    content: str
    background: File
