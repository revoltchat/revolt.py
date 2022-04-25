from __future__ import annotations
from distutils import command

from typing import TYPE_CHECKING, Any, Optional

from .command import Command

if TYPE_CHECKING:
    from .client import CommandsClient

__all__ = ("Cog", "CogMeta")

class CogMeta(type):
    _commands: list[Command]
    qualified_name: str

    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any], *, qualified_name: Optional[str] = None):
        commands: list[Command] = []
        self = super().__new__(cls, name, bases, attrs)

        for base in reversed(self.__mro__):
            for value in base.__dict__.values():
                if isinstance(value, Command):
                    commands.append(value)


        self._commands = commands
        self.qualified_name = qualified_name or name
        return self

class Cog(metaclass=CogMeta):
    _commands: list[Command]
    qualified_name: str

    def cog_load(self):
        """A special method that is called when the cog gets loaded."""
        pass

    def cog_unload(self):
        """A special method that is called when the cog gets removed."""
        pass

    def _inject(self, client: CommandsClient):  
        client.cogs[self.qualified_name] = self

        for command in self._commands:
            command.cog = self
            client.add_command(command)

        self.cog_load()

    def _uninject(self, client: CommandsClient):
        for name, command in client.all_commands.copy().items():
            if command in self._commands:
                del client.all_commands[name]

        self.cog_unload()

    @property
    def commands(self) -> list[Command]:
        return self._commands
