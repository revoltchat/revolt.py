from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Embed as EmbedPayload


__all__ = ("Embed",)

class Embed:
    @classmethod
    def from_dict(cls, data: EmbedPayload):
        ...

    def to_dict(self) -> EmbedPayload:
        ...
