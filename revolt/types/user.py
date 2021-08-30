from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Literal

if TYPE_CHECKING:
    from .file import File

Relation = Literal["Blocked", "BlockedOther", "Friend", "Incoming", "None", "Outgoing", "User"]

class UserBot(TypedDict):
    owner: str

class _OptionalStatus(TypedDict, total=False):
    text: str

class Status(_OptionalStatus):
    presence: Literal["Busy", "Idle", "Invisible", "Online"]

class UserRelation(TypedDict):
    status: Relation
    _id: str

class _OptionalUser(TypedDict, total=False):
    avatar: File
    relations: list[UserRelation]
    badges: int
    status: Status
    relationship: Relation
    online: bool
    flags: int
    bot: UserBot

class User(_OptionalUser):
    _id: str
    username: str
