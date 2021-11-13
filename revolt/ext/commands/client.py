from __future__ import annotations

import re
import traceback
from typing import Any, Callable, Union

import revolt

from .command import Command
from .context import Context
from .errors import CheckError, CommandNotFound
from .view import StringView

__all__ = (
    "CommandsMeta",
    "CommandsClient"
)

quote_regex = re.compile(r"[\"']")
chunk_regex = re.compile(r"\S+")


class CommandsMeta(type):
    _commands: list[Command]

    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any]):
        commands: list[Command] = []
        self = super().__new__(cls, name, bases, attrs)

        for base in reversed(self.__mro__):
            for value in base.__dict__.values():
                if isinstance(value, Command):
                    commands.append(value)

        self._commands = commands

        for command in commands:
            command._client = self  # type: ignore

        return self

class CommandsClient(revolt.Client, metaclass=CommandsMeta):
    """Main class that adds commands, this class should be subclassed along with `revolt.Client`."""

    _commands: list[Command]

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

        view = self.get_view(message)(content)

        try:
            command_name = view.get_next_word()
        except StopIteration:
            return

        context_cls = self.get_context(message)

        try:
            command = self.get_command(command_name)
        except KeyError:
            context = context_cls(None, command_name, view, message, self)
            return self.dispatch("command_error", context, CommandNotFound(command_name))

        context = context_cls(command, command_name, view, message, self)

        try:
            self.dispatch("command", context)

            if not await self.bot_check(context):
                raise CheckError(f"the global check for the command failed")

            if not await context.can_run():
                raise CheckError(f"the check(s) for the command failed")

            output = await context.invoke()
            self.dispatch("after_command_invoke", context, output)

            return output
        except Exception as e:
            self.dispatch("command_error", context, e)

    @staticmethod
    async def on_command_error(ctx: Context, error: Exception):
        traceback.print_exception(type(error), error, error.__traceback__)

    on_message = process_commands

    async def bot_check(self, context: Context) -> bool:
        """A global check for the bot that stops commands from running on certain criteria.

        Parameters
        -----------
        context: :class:`Context`
            The context for the invokation of the command

        Returns
        --------
        :class:`bool` represents if the command should run or not
        """

        return True
