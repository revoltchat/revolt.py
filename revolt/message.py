from __future__ import annotations

from typing import TYPE_CHECKING

from .asset import Asset
from .channel import Messageable
from .embed import Embed

if TYPE_CHECKING:
    from .state import State
    from .types import Message as MessagePayload


__all__ = ("Message",)

class Message:
    """Represents a message
    
    Attributes
    -----------
    id: :class:`str`
        The id of the message
    content: :class:`str`
        The content of the message, this will not include system message's content
    attachments: list[:class:`Asset`]
        The attachments of the message
    embeds: list[:class:`Embed`]
        The embeds of the message
    channel: :class:`Messageable`
        The channel the message was sent in
    server: :class:`Server`
        The server the message was sent in
    author: Union[:class:`Member`, :class:`User`]
        The author of the message, will be :class:`User` in DMs
    """
    __slots__ = ("state", "id", "content", "attachments", "embeds", "channel", "server", "author")
    
    def __init__(self, data: MessagePayload, state: State):
        self.state = state
        
        self.id = data["_id"]
        self.content = data["content"]
        self.attachments = [Asset(attachment, state) for attachment in data.get("attachments", [])]
        self.embeds = [Embed.from_dict(embed) for embed in data.get("embeds", [])]

        channel = state.get_channel(data["channel"])
        assert isinstance(channel, Messageable)
        self.channel = channel

        self.server = self.channel and self.channel.server
        
        if self.server:
            author = state.get_member(self.server.id, data["author"])
        else:
            author = state.get_user(data["author"])

        assert author
        self.author = author
