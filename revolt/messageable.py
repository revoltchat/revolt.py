from __future__ import annotations

from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from .state import State
    from .message import Message
    from .embed import Embed
    from .file import File

class Messageable:
    id: str

    def __init__(self, state: State):
        self.state = state

    async def send(self, content: Optional[str] = None, embeds: Optional[list[Embed]] = None, embed: Optional[Embed] = None, attachments: Optional[list[File]] = None) -> Message:
        if embed:
            embeds = [embed]

        embed_payload = [embed.to_dict() for embed in embeds] if embeds else None

        message = await self.state.http.send_message(self.id, content, embed_payload, attachments)
        return self.state.add_message(message)
