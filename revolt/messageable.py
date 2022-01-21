from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .enums import SortType

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

    async def _get_channel_id(self) -> str:
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

        message = await self.state.http.send_message(await self._get_channel_id(), content, embed_payload, attachments, reply_payload, masquerade_payload)
        return self.state.add_message(message)


    async def fetch_message(self, message_id: str) -> Message:
        """Fetches a message from the channel

        Parameters
        -----------
        message_id: :class:`str`
            The id of the message you want to fetch

        Returns
        --------
        :class:`Message`
            The message with the matching id
        """
        payload = await self.state.http.fetch_message(await self._get_channel_id(), message_id)
        return Message(payload, self.state)

    async def history(self, *, sort: SortType = SortType.latest, limit: int = 100, before: Optional[str] = None, after: Optional[str] = None, nearby: Optional[str] = None) -> list[Message]:
        """Fetches multiple messages from the channel's history

        Parameters
        -----------
        sort: :class:`SortType`
            The order to sort the messages in
        limit: :class:`int`
            How many messages to fetch
        before: Optional[:class:`str`]
            The id of the message which should come *before* all the messages to be fetched
        after: Optional[:class:`str`]
            The id of the message which should come *after* all the messages to be fetched
        nearby: Optional[:class:`str`]
            The id of the message which should be nearby all the messages to be fetched

        Returns
        --------
        list[:class:`Message`]
            The messages found in order of the sort parameter
        """
        payloads = await self.state.http.fetch_messages(await self._get_channel_id(), sort=sort, limit=limit, before=before, after=after, nearby=nearby)
        return [Message(payload, self.state) for payload in payloads]

    async def search(self, query: str, *, sort: SortType = SortType.latest, limit: int = 100, before: Optional[str] = None, after: Optional[str] = None) -> list[Message]:
        """searches the channel for a query

        Parameters
        -----------
        query: :class:`str`
            The query to search for in the channel
        sort: :class:`SortType`
            The order to sort the messages in
        limit: :class:`int`
            How many messages to fetch
        before: Optional[:class:`str`]
            The id of the message which should come *before* all the messages to be fetched
        after: Optional[:class:`str`]
            The id of the message which should come *after* all the messages to be fetched

        Returns
        --------
        list[:class:`Message`]
            The messages found in order of the sort parameter
        """
        payloads = await self.state.http.search_messages(await self._get_channel_id(), query, sort=sort, limit=limit, before=before, after=after)
        return [Message(payload, self.state) for payload in payloads]
