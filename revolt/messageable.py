from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .embed import Embed
    from .file import File
    from .message import Message
    from .state import State


__all__ = ("Messageable",)

class Messageable:
    """Base class for all channels that you can send messages in
    
    Attributes
    -----------
    id: :class:`str`
        The id of the channel
    """
    id: str
    state: State

    __slots__ = ()

    async def send(self, content: Optional[str] = None, *, embeds: Optional[list[Embed]] = None, embed: Optional[Embed] = None, attachments: Optional[list[File]] = None) -> Message:
        """Sends a message in a channel, you must send at least one of either `content`, `embeds` or `attachments`

        Parameters
        -----------
        content: Optional[:class:`str`]
            The content of the message, this will not include system message's content
        attachments: Optional[list[:class:`File`]]
            The attachments of the message
        embeds: Optional[list[:class:`Embed`]]
            The embeds of the message

        Returns
        --------
        :class:`Message`
            The message that was just sent
        """
        if embed:
            embeds = [embed]

        embed_payload = [embed.to_dict() for embed in embeds] if embeds else None

        message = await self.state.http.send_message(self.id, content, embed_payload, attachments)
        return self.state.add_message(message)
