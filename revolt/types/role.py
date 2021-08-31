from __future__ import annotations

from typing import Tuple, TypedDict

Permission = Tuple[int, int]

class _RoleOptional(TypedDict, total=False):
    colour: str
    hoist: bool
    rank: int

class Role(_RoleOptional):
    name: str
    permissions: Permission
