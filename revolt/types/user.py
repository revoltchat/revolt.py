from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Literal

if TYPE_CHECKING:
    from .file import File

class UserBot(TypedDict):
    owner: str

class Status(TypedDict, total=False):
    text: str
    presence: Literal["Busy", "Idle", "Invisible", "Online"]

class _OptionalUser(TypedDict, total=False):
    avatar: File
    relations: list
    badges: int
    status: Status
    relationship: Literal["Blocked", "BlockedOther", "Friend", "Incoming", "None", "Outgoing", "User"]
    online: bool
    flags: int
    bot: UserBot

class User(_OptionalUser):
    _id: str
    username: str
