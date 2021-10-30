from __future__ import annotations

from typing import Any, Callable, Union
import re

import revolt
import traceback

from .view import StringView
from .command import Command
from .context import Context
from .errors import CommandNotFound


__all__ = (
    "CommandsMeta",
    "CommandsMixin"
)

quote_regex = re.compile(r"[\"']")
chunk_regex = re.compile(r"\S+")


class CommandsMeta(type):
    _commands: list[Command]

    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any]):
        commands: list[Command] = []

        for value in attrs.values():
            if isinstance(value, Command):
                commands.append(value)

        self = super().__new__(cls, name, bases, attrs)
        self._commands = commands

        for command in commands:
            command._client = self  # type: ignore

        return self

class CommandsMixin(metaclass=CommandsMeta):
    """Main class that adds commands, this class should be subclassed along with `revolt.Client`."""

    _commands: list[Command]
    dispatch: Callable[..., None]

    def __init__(self, *args, **kwargs):
        self.all_commands: dict[str, Command] = {}

        for command in self._commands:
            self.all_commands[command.name] = command

            for alias in command.aliases:
                self.all_commands[alias] = command

        super().__init__(*args, **kwargs)

    @property
    def commands(self) -> list[Command]:
        return list(set(self.all_commands.values()))

    async def get_prefix(self, message: revolt.Message) -> Union[str, list[str]]:
        """Overwrite this function to set the prefix used for commands, this function is called for every message.

        Parameters
        -----------
        message: :class:`Message`
            The message that was sent

        Returns
        --------
        Union[:class:`str`, list[:class:`str`]]
            The prefix(s) for the commands
        """
        raise NotImplementedError

    def get_command(self, name: str) -> Command:
        """Gets a command.

        Parameters
        -----------
        name: :class:`str`
            The name or alias of the command

        Returns
        --------
        :class:`Command`
            The command with the name
        """
        return self.all_commands[name]

    def add_command(self, name: str, command: Command):
        """Adds a command, this is typically only used for dynamic commands, you should use the `commands.command` decorator for most usecases.

        Parameters
        -----------
        name: :class:`str`
            The name or alias of the command
        command: :class:`Command`
            The command to be added
        """
        self.all_commands[name] = command

    def get_view(self, message: revolt.Message) -> type[StringView]:
        return StringView

    def get_context(self, message: revolt.Message) -> type[Context]:
        return Context

    async def process_commands(self, message: revolt.Message) -> Any:
        """Processes commands, if you overwrite `Client.on_message` you should manually call this function inside the event.

        Parameters
        -----------
        message: :class:`Message`
            The message to process commands on

        Returns
        --------
        Any
            The return of the command, if any
        """
        content = message.content

        if not isinstance(content, str):
            return

        prefixes = await self.get_prefix(message)

        if isinstance(prefixes, str):
            prefixes = [prefixes]

        for prefix in prefixes:
            if content.startswith(prefix):
                content = content[len(prefix):]
                break
        else:
            return

        if not content:
            return

        view = StringView(content)

        try:
            command_name = view.get_next_word()
        except StopIteration:
            return

        context_cls = self.get_context(message)

        try:
            command = self.get_command(command_name)
        except KeyError:
            context = context_cls(None, command_name, view, message)
            return self.dispatch("command_error", context, CommandNotFound(command_name))

        context = context_cls(command, command_name, view, message)

        try:
            return await context.invoke()
        except Exception as e:
            self.dispatch("command_error", context, e)


    @staticmethod
    async def command_error(ctx: Context, error: Exception):
        traceback.print_exception(type(error), error, error.__traceback__)

    on_message = process_commands
