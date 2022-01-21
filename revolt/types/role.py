from __future__ import annotations

from typing import TypedDict

__all__ = (
    "Permission",
    "Role",
)

Permission = tuple[int, int]

class Role(TypedDict):
    name: str
    permissions: Permission
