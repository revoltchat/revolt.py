from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional

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
    edited_at: Optional[:class:`datetime.datetime`]
        The time at which the message was edited, will be None if the message has not been edited
    """
    __slots__ = ("state", "id", "content", "attachments", "embeds", "channel", "server", "author", "edited_at")
    
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

        self.edited_at: Optional[datetime.datetime] = None

    def _update(self, *, content: Optional[str] = None, edited_at: Optional[str] = None) -> Message:
        if content:
            self.content = content

        if edited_at:
            self.edited_at = datetime.datetime.strptime(edited_at, "%Y-%m-%dT%H:%M:%S.%f%z")
            # strptime is used here instead of fromisoformat because of its inability to parse `Z` (Zulu or UTC time) in the RFCC 3339 format provided by API

        return self

    async def edit(self, *, content: str) -> None:
        """Edits the message. The bot can only edit its own message
        Parameters
        -----------
        content: :class:`str`
            The new content of the message
        """
        await self.state.http.edit_message(self.channel.id, self.id, content)

    async def delete(self) -> None:
        """Deletes the message. The bot can only delete its own messages and messages it has permission to delete """
        await self.state.http.delete_message(self.channel.id, self.id)
