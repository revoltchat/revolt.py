from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .permissions import Overwrite

__all__ = (
    "Role",
)

class Role(TypedDict):
    name: str
    permissions: Overwrite
    colour: NotRequired[str]
    hoist: NotRequired[bool]
    rank: int
