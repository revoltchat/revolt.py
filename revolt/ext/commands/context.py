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
    """
    __slots__ = ("command", "invoked_with", "message")

    def __init__(self, command: Optional[Command], invoked_with: str, message: revolt.Message):
        self.command = command
        self.invoked_with = invoked_with
        self.message = message

    async def invoke(self, args: list[str]) -> Any:
        """Invokes the command, this is equal to `await context.command.invoke(context, args)`.

        .. note:: If the command is `None`, this function will do nothing.

        Parameters
        -----------
        args: list[:class:`str`]
            The args being passed to the command
        """
        if command := self.command:
            return await command.invoke(self, args)

    @copy_doc(revolt.Messageable.send)
    async def send(self, content: Optional[str] = None, *, embeds: Optional[list[revolt.Embed]] = None, embed: Optional[revolt.Embed] = None, attachments: Optional[list[revolt.File]] = None) -> revolt.Message:
        return await self.message.channel.send(content, embeds=embeds, embed=embed, attachments=attachments)
