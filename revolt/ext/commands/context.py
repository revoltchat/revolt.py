from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

import revolt
from revolt.utils import maybe_coroutine

from .command import Command

if TYPE_CHECKING:
    from .client import CommandsClient
    from .view import StringView

__all__ = (
    "Context",
)

class Context(revolt.Messageable):
    """Stores metadata the commands execution.

    Attributes
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
        The positional arguments being passed to the command
    kwargs: dict[:class:`str`, Any]
        The keyword arguments being passed to the command
    client: :class:`CommandsClient`
        The revolt client
    """
    __slots__ = ("command", "invoked_with", "args", "message", "server", "channel", "author", "view", "kwargs", "state", "client")

    def _get_channel_id(self) -> str:
        return self.channel.id

    def __init__(self, command: Optional[Command], invoked_with: str, view: StringView, message: revolt.Message, client: CommandsClient):
        self.command = command
        self.invoked_with = invoked_with
        self.view = view
        self.message = message
        self.client = client
        self.args = []
        self.kwargs = {}
        self.server = message.server
        self.channel = message.channel
        self.author = message.author
        self.state = message.state

    async def invoke(self) -> Any:
        """Invokes the command, this is equal to `await command.invoke(context, context.args)`.

        .. note:: If the command is `None`, this function will do nothing.

        Parameters
        -----------
        args: list[:class:`str`]
            The args being passed to the command
        """

        if command := self.command:
            await command.parse_arguments(self)

            return await command.invoke(self, *self.args, **self.kwargs)

    async def can_run(self) -> bool:
        """Runs all of the commands checks, and returns true if all of them pass"""
        return all([await maybe_coroutine(check, self) for check in (self.command.checks if self.command else [])])

