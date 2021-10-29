from __future__ import annotations

from typing import Any, Optional

import revolt
from revolt.utils import copy_doc

from .command import Command

__all__ = (
    "Context",
)

class Context:
    """Stores metadata the commands execution.

    Parameters
    -----------
    command: Optional[:class:`Command`]
        The command, this can be `None` when no command was found and the error handler is being executed
    invoked_with: :class:`str`
        The command name that was used, this can be an alias, the commands name or a command that doesnt exist
    message: :class:`Message`
        The message that was sent to invoke the command
    channel: :class:`Messageable`
        The channel the command was invoked in
    server: :class:`Server`
        The server the command was invoked in
    author: Union[:class:`Member`, :class:`User`]
        The user or member that invoked the commad, will be :class:`User` in DMs
    args: list[:class:`str`]
        The arguments being passed to the command
    """
    __slots__ = ("command", "invoked_with", "args", "message", "server", "channel", "author")

    def __init__(self, command: Optional[Command], invoked_with: str, args: list[str], message: revolt.Message):
        self.command = command
        self.invoked_with = invoked_with
        self.args = args
        self.message = message
        self.server = message.server
        self.channel = message.channel
        self.author = message.author

    async def invoke(self) -> Any:
        """Invokes the command, this is equal to `await command.invoke(context, context.args)`.

        .. note:: If the command is `None`, this function will do nothing.

        Parameters
        -----------
        args: list[:class:`str`]
            The args being passed to the command
        """
        if command := self.command:
            return await command.invoke(self, self.args)

    @copy_doc(revolt.Messageable.send)
    async def send(self, content: Optional[str] = None, *, embeds: Optional[list[revolt.Embed]] = None, embed: Optional[revolt.Embed] = None, attachments: Optional[list[revolt.File]] = None, replies: Optional[list[revolt.MessageReply]] = None) -> revolt.Message:
        return await self.message.channel.send(content, embeds=embeds, embed=embed, attachments=attachments)
