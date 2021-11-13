from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, NamedTuple, Optional

from .asset import Asset, PartialAsset
from .channel import Messageable
from .embed import Embed

if TYPE_CHECKING:
    from .state import State
    from .types import Masquerade as MasqueradePayload
    from .types import Message as MessagePayload
    from .types import MessageReplyPayload


__all__ = (
    "Message",
    "MessageReply",
    "Masquerade"
)

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
    mentions: list[Union[:class:`Member`, :class:`User`]]
        The users or members that where mentioned in the message
    replies: list[:class:`Message`]
        The message's this message has replied to, this may not contain all the messages if they are outside the cache
    reply_ids: list[:class:`str`]
        The message's ids this message has replies to
    """
    __slots__ = ("state", "id", "content", "attachments", "embeds", "channel", "server", "author", "edited_at", "mentions", "replies", "reply_ids")

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

        self.author = author

        if masquerade := data.get("masquerade"):
            if name := masquerade.get("name"):
                self.author.masquerade_name = name

            if avatar := masquerade.get("avatar"):
                self.author.masquerade_avatar = PartialAsset(avatar, state)

        if edited_at := data.get("edited"):
            self.edited_at: Optional[datetime.datetime] = datetime.datetime.strptime(edited_at["$date"], "%Y-%m-%dT%H:%M:%S.%f%z")

        if self.server:
            self.mentions = [self.server.get_member(member_id) for member_id in data.get("mentions", [])]
        else:
            self.mentions = [state.get_user(member_id) for member_id in data.get("mentions", [])]

        self.replies = []
        self.reply_ids = []

        for reply in data.get("replies", []):
            try:
                message = state.get_message(reply)
                self.replies.append(message)
            except KeyError:
                pass

            self.reply_ids.append(reply)

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

class MessageReply(NamedTuple):
    """A namedtuple which represents a reply to a message.

    Parameters
    -----------
    message: :class:`Message`
        The message being replied to.
    mention: :class:`bool`
        Whether the reply should mention the author of the message. Defaults to false.
    """
    message: Message
    mention: bool = False

    def to_dict(self) -> MessageReplyPayload:
        return { "id": self.message.id, "mention": self.mention }

class Masquerade(NamedTuple):
    """A namedtuple which represents a message's masquerade.

    Parameters
    -----------
    name: Optional[:class:`str`]
        The name to display for the message
    avatar: Optional[:class:`str`]
        The avatar's url to display for the message
    """
    name: Optional[str] = None
    avatar: Optional[str] = None

    def to_dict(self) -> MasqueradePayload:
        output: MasqueradePayload = {}

        if name := self.name:
            output["name"] = name

        if avatar := self.avatar:
            output["avatar"] = avatar

        return output
