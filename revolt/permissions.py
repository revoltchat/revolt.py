from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Permission as PermissionTuple


__all__ = ("Permissions",)

class Permissions:
    def __init__(self, permission_tuple: PermissionTuple):
        ...
