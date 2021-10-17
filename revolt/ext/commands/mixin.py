from __future__ import annotations

from typing import Any, Callable, Union, TYPE_CHECKING
from abc import ABC
import revolt
from shlex import shlex

from .context import Context
from .command import Command
from .errors import CommandNotFound

__all__ = (
    "CommandsMeta",
    "CommandsMixin"
)

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
            command._client = self  # typing: ignore

        return self

class CommandsMixin(metaclass=CommandsMeta):
    _commands: list[Command]
    dispatch: Callable[..., None]

    def __init__(self, *args, **kwargs):
        self.all_commands = {}

        for command in self._commands:
            self.all_commands[command.name] = command

            for alias in command.aliases:
                self.all_commands[alias] = command

        super().__init__(*args, **kwargs)

    @property
    def commands(self) -> list[Command]:
        return list(set(self.all_commands.values()))

    async def get_prefix(self, message: revolt.Message) -> Union[str, list[str]]:
        raise NotImplementedError

    def get_command(self, name: str) -> Command:
        return self.all_commands[name]

    def add_command(self, name: str, command: Command):
        self.all_commands[name] = command

    def split_content(self, content: str) -> list[str]:
        lex = shlex(content, posix=True)
        lex.commenters = ""
        lex.whitespace_split = True

        return list(lex)

    async def process_commands(self, message: revolt.Message):
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

        command_name, *args = self.split_content(content)

        try:
            command = self.get_command(command_name)
        except KeyError:
            return self.dispatch("command_error", Context(None, command_name, message), CommandNotFound(command_name))

        context = Context(command, command_name, message)

        try:
            await context.invoke(args)
        except Exception as e:
            self.dispatch("command_error", context, e)

    on_message = process_commands
