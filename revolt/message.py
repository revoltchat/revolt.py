from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, Optional

from .asset import Asset, PartialAsset
from .channel import Messageable
from .embed import SendableEmbed, to_embed
from .utils import Ulid

if TYPE_CHECKING:
    from .state import State
    from .types import Embed as EmbedPayload
    from .types import Masquerade as MasqueradePayload
    from .types import Message as MessagePayload
    from .types import Interactions as InteractionsPayload
    from .types import MessageReplyPayload
    from .server import Server
    from .user import User

__all__ = (
    "Message",
    "MessageReply",
    "Masquerade",
    "MessageInteractions"
)

class Message(Ulid):
    """Represents a message

    Attributes
    -----------
    id: :class:`str`
        The id of the message
    content: :class:`str`
        The content of the message, this will not include system message's content
    attachments: list[:class:`Asset`]
        The attachments of the message
    embeds: list[Union[:class:`WebsiteEmbed`, :class:`ImageEmbed`, :class:`TextEmbed`, :class:`NoneEmbed`]]
        The embeds of the message
    channel: :class:`Messageable`
        The channel the message was sent in
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
    reactions: dict[str, list[:class:`User`]]
        The reactions on the message
    interactions: Optional[:class:`MessageInteractions`]
        The interactions on the message, if any
    """
    __slots__ = ("state", "id", "content", "attachments", "embeds", "channel", "author", "edited_at", "mentions", "replies", "reply_ids", "reactions", "interactions")

    def __init__(self, data: MessagePayload, state: State):
        self.state = state

        self.id = data["_id"]
        self.content = data.get("content", "")
        self.attachments = [Asset(attachment, state) for attachment in data.get("attachments", [])]
        self.embeds = [to_embed(embed, state) for embed in data.get("embeds", [])]

        channel = state.get_channel(data["channel"])
        assert isinstance(channel, Messageable)
        self.channel = channel

        if server_id := self.channel.server_id:
            author = state.get_member(server_id, data["author"])
        else:
            author = state.get_user(data["author"])

        self.author = author

        if masquerade := data.get("masquerade"):
            if name := masquerade.get("name"):
                self.author.masquerade_name = name

            if avatar := masquerade.get("avatar"):
                self.author.masquerade_avatar = PartialAsset(avatar, state)

        if edited_at := data.get("edited"):
            self.edited_at: Optional[datetime.datetime] = datetime.datetime.strptime(edited_at, "%Y-%m-%dT%H:%M:%S.%f%z")

        if self.server:
            self.mentions = [self.server.get_member(member_id) for member_id in data.get("mentions", [])]
        else:
            self.mentions = [state.get_user(member_id) for member_id in data.get("mentions", [])]

        self.replies: list[Message] = []
        self.reply_ids: list[str] = []

        for reply in data.get("replies", []):
            try:
                message = state.get_message(reply)
                self.replies.append(message)
            except LookupError:
                pass

            self.reply_ids.append(reply)

        reactions = data.get("reactions", {})

        self.reactions: dict[str, list[User]] = {}

        for emoji, users in reactions.items():
            self.reactions[emoji] = [self.state.get_user(user_id) for user_id in users]

        if interactions := data.get("interactions"):
            self.interactions = MessageInteractions(reactions=interactions.get("reactions"), restrict_reactions=interactions.get("restrict_reactions", False))
        else:
            self.interactions = None

    def _update(self, *, content: Optional[str] = None, embeds: Optional[list[EmbedPayload]] = None, edited: int):
        if content:
            self.content = content

        self.edited = datetime.datetime.fromtimestamp(edited / 1000)

        if embeds:
            self.embeds = [to_embed(embed, self.state) for embed in embeds]

    async def edit(self, *, content: Optional[str] = None, embeds: Optional[list[SendableEmbed]] = None) -> None:
        """Edits the message. The bot can only edit its own message
        Parameters
        -----------
        content: :class:`str`
            The new content of the message
        """

        new_embeds = [embed.to_dict() for embed in embeds] if embeds else None

        await self.state.http.edit_message(self.channel.id, self.id, content, new_embeds)

    async def delete(self) -> None:
        """Deletes the message. The bot can only delete its own messages and messages it has permission to delete """
        await self.state.http.delete_message(self.channel.id, self.id)

    def reply(self, *args: Any, mention: bool = False, **kwargs: Any):
        """Replies to this message, equivilant to:

        .. code-block:: python

            await channel.send(..., replies=[MessageReply(message, mention)])

        """
        return self.channel.send(*args, **kwargs, replies=[MessageReply(self, mention)])

    async def add_reaction(self, emoji: str):
        await self.state.http.add_reaction(self.channel.id, self.id, emoji)

    async def remove_reaction(self, emoji: str, user: Optional[User] = None, remove_all: bool = False):
        await self.state.http.remove_reaction(self.channel.id, self.id, emoji, user.id if user else None, remove_all)

    async def remove_all_reactions(self):
        await self.state.http.remove_all_reactions(self.channel.id, self.id)


    @property
    def server(self) -> Server:
        """:class:`Server` The server this voice channel belongs too"""
        return self.channel.server

class MessageReply:
    """represents a reply to a message.

    Parameters
    -----------
    message: :class:`Message`
        The message being replied to.
    mention: :class:`bool`
        Whether the reply should mention the author of the message. Defaults to false.
    """
    __slots__ = ("message", "mention")

    def __init__(self, message: Message, mention: bool = False):
        self.message = message
        self.mention = mention

    def to_dict(self) -> MessageReplyPayload:
        return { "id": self.message.id, "mention": self.mention }

class Masquerade:
    """represents a message's masquerade.

    Parameters
    -----------
    name: Optional[:class:`str`]
        The name to display for the message
    avatar: Optional[:class:`str`]
        The avatar's url to display for the message
    colour: Optional[:class:`str`]
        The colour of the name, similar to role colours
    """
    __slots__ = ("name", "avatar", "colour")

    def __init__(self, name: Optional[str] = None, avatar: Optional[str] = None, colour: Optional[str] = None):
        self.name = name
        self.avatar = avatar
        self.colour = colour

    def to_dict(self) -> MasqueradePayload:
        output: MasqueradePayload = {}

        if name := self.name:
            output["name"] = name

        if avatar := self.avatar:
            output["avatar"] = avatar

        if colour := self.colour:
            output["colour"] = colour

        return output

class MessageInteractions:
    """Represents a message's interactions, this is for allowing preset reactions and restricting adding reactions to only those.

    Parameters
    -----------
    reactions: Optional[list[:class:`str`]]
        The preset reactions on the message
    restrict_reactions: bool
        Whether or not users can only react to the interaction's reactions
    """
    __slots__ = ("reactions", "restrict_reactions")

    def __init__(self, *, reactions: Optional[list[str]] = None, restrict_reactions: bool = False):
        self.reactions = reactions
        self.restrict_reactions = restrict_reactions

    def to_dict(self):
        output: InteractionsPayload = {}

        if reactions := self.reactions:
            output["reactions"] = reactions

        if restrict_reactions := self.restrict_reactions:
            output["restrict_reactions"] = restrict_reactions

        return output
