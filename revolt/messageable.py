from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .embed import Embed
    from .file import File
    from .message import Masquerade, Message, MessageReply
    from .state import State


__all__ = ("Messageable",)

class Messageable:
    """Base class for all channels that you can send messages in

    Attributes
    -----------
    id: :class:`str`
        The id of the channel
    """
    state: State

    __slots__ = ()

    def _get_channel_id(self) -> str:
        raise NotImplementedError

    async def send(self, content: Optional[str] = None, *, embeds: Optional[list[Embed]] = None, embed: Optional[Embed] = None, attachments: Optional[list[File]] = None, replies: Optional[list[MessageReply]] = None, reply: Optional[MessageReply] = None, masquerade: Optional[Masquerade] = None) -> Message:
        """Sends a message in a channel, you must send at least one of either `content`, `embeds` or `attachments`

        Parameters
        -----------
        content: Optional[:class:`str`]
            The content of the message, this will not include system message's content
        attachments: Optional[list[:class:`File`]]
            The attachments of the message
        embeds: Optional[list[:class:`Embed`]]
            The embeds of the message
        replies: Optional[list[:class:`MessageReply`]]
            The list of messages to reply to.

        Returns
        --------
        :class:`Message`
            The message that was just sent
        """
        if embed:
            embeds = [embed]

        if reply:
            replies = [reply]

        embed_payload = [embed.to_dict() for embed in embeds] if embeds else None
        reply_payload = [reply.to_dict() for reply in replies] if replies else None
        masquerade_payload = masquerade.to_dict() if masquerade else None

        message = await self.state.http.send_message(self._get_channel_id(), content, embed_payload, attachments, reply_payload, masquerade_payload)
        return self.state.add_message(message)
