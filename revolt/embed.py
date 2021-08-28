from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .payloads import Embed as EmbedPayload

class Embed:
    @classmethod
    def from_dict(cls, data: EmbedPayload):
        ...

    def to_dict(self) -> EmbedPayload:
        ...
