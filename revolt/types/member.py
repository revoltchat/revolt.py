from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .file import File


__all__ = ("Member", "MemberID")

class MemberID(TypedDict):
    server: str
    user: str

class Member(TypedDict):
    _id: MemberID
    nickname: NotRequired[str]
    avatar: NotRequired[File]
    roles: NotRequired[list[str]]
    joined_at: int | str
    timeout: NotRequired[str | int]
