from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .enums import SortType

if TYPE_CHECKING:
    from .embed import SendableEmbed
    from .file import File
    from .message import Masquerade, Message, MessageInteractions, MessageReply
    from .state import State
    from .types.http import MessageWithUserData


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

    async def send(self, content: Optional[str] = None, *, embeds: Optional[list[SendableEmbed]] = None, embed: Optional[SendableEmbed] = None, attachments: Optional[list[File]] = None, replies: Optional[list[MessageReply]] = None, reply: Optional[MessageReply] = None, masquerade: Optional[Masquerade] = None, interactions: Optional[MessageInteractions] = None) -> Message:
        """Sends a message in a channel, you must send at least one of either `content`, `embeds` or `attachments`

        Parameters
        -----------
        content: Optional[:class:`str`]
            The content of the message, this will not include system message's content
        attachments: Optional[list[:class:`File`]]
            The attachments of the message
        embed: Optional[:class:`SendableEmbed`]
            The embed to send with the message
        embeds: Optional[list[:class:`SendableEmbed`]]
            The embeds to send with the message
        replies: Optional[list[:class:`MessageReply`]]
            The list of messages to reply to.
        masquerade: Optional[:class:`Masquerade`]
            The masquerade for the message, this can overwrite the username and avatar shown
        interactions: Optional[:class:`MessageInteractions`]
            The interactions for the message

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
        interactions_payload = interactions.to_dict() if interactions else None

        message = await self.state.http.send_message(await self._get_channel_id(), content, embed_payload, attachments, reply_payload, masquerade_payload, interactions_payload)
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
        from .message import Message

        payload = await self.state.http.fetch_message(await self._get_channel_id(), message_id)
        return Message(payload, self.state)

    def _add_missing_users(self, payload: MessageWithUserData):
        for user in payload["users"]:
            if user["_id"] not in self.state.users:
                self.state.add_user(user)

        if members := payload.get("members", []):
            server = self.state.get_server(members[0]["_id"]["server"])

            for member in members:
                if member["_id"]["user"] not in server._members:
                    server._add_member(member)

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
        from .message import Message

        payload = await self.state.http.fetch_messages(await self._get_channel_id(), sort=sort, limit=limit, before=before, after=after, nearby=nearby, include_users=True)
        self._add_missing_users(payload)

        return [Message(msg, self.state) for msg in payload["messages"]]

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
        from .message import Message

        payload = await self.state.http.search_messages(await self._get_channel_id(), query, sort=sort, limit=limit, before=before, after=after, include_users=True)
        self._add_missing_users(payload)

        return [Message(msg, self.state) for msg in payload["messages"]]

    async def delete_messages(self, messages: list[Message]) -> None:
        """Bulk deletes messages from the channel

        .. note:: The messages must have been sent in the last 7 days.

        Parameters
        -----------
        messages: list[:class:`Message`]
            The messages for deletion, this can be up to 100 messages
        """

        await self.state.http.delete_messages(await self._get_channel_id(), [message.id for message in messages])
