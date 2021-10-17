from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .file import File


__all__ = ("Member",)

class _MemberOptional(TypedDict, total=False):
    nickname: str
    avatar: File
    roles: list[str]

class MemberID(TypedDict):
    server: str
    user: str

class Member(_MemberOptional):
    _id: MemberID
