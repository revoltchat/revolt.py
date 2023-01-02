from __future__ import annotations

from typing import Any, Generic, Optional, cast

from .command import Command
from .utils import ClientT


__all__ = ("Cog", "CogMeta")

class CogMeta(type, Generic[ClientT]):
    _commands: list[Command[ClientT]]
    qualified_name: str

    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any], *, qualified_name: Optional[str] = None):
        commands: list[Command[ClientT]] = []
        self = super().__new__(cls, name, bases, attrs)

        for base in reversed(self.__mro__):
            for value in base.__dict__.values():
                if isinstance(value, Command):
                    commands.append(cast(Command[ClientT], value))  # cant verify generic at runtime so must cast


        self._commands = commands
        self.qualified_name = qualified_name or name
        return self

class Cog(Generic[ClientT], metaclass=CogMeta):
    _commands: list[Command[ClientT]]
    qualified_name: str

    def cog_load(self):
        """A special method that is called when the cog gets loaded."""
        pass

    def cog_unload(self):
        """A special method that is called when the cog gets removed."""
        pass

    def _inject(self, client: ClientT):
        client.cogs[self.qualified_name] = self

        for command in self._commands:
            command.cog = self
            client.add_command(command)

        self.cog_load()

    def _uninject(self, client: ClientT):
        for name, command in client.all_commands.copy().items():
            if command in self._commands:
                del client.all_commands[name]

        self.cog_unload()

    @property
    def commands(self) -> list[Command[ClientT]]:
        return self._commands
