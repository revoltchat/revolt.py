from __future__ import annotations

from typing import Any, Callable, Coroutine, Generic, Optional, TypeVar, cast
from typing_extensions import ParamSpec, Self

from revolt.errors import RevoltError

from .command import Command
from .utils import ClientT_D

P = ParamSpec("P")
R = TypeVar("R")

__all__ = ("Cog", "CogMeta")

class CogMeta(type, Generic[ClientT_D]):
    _cog_commands: list[Command[ClientT_D]]
    _cog_listeners: dict[str, list[str]]
    qualified_name: str

    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any], *, qualified_name: Optional[str] = None, extras: dict[str, Any] | None = None) -> Self:
        commands: list[Command[ClientT_D]] = []
        listeners: dict[str, list[str]] = {}

        self = super().__new__(cls, name, bases, attrs)
        extras = extras or {}

        for base in reversed(self.__mro__):
            for key, value in base.__dict__.items():
                if isinstance(value, Command):
                    for extra_key, extra_value in extras.items():
                        setattr(value, extra_key, extra_value)

                    commands.append(cast(Command[ClientT_D], value))  # cant verify generic at runtime so must cast

                elif event_name := getattr(value, "__listener_name", None):
                    listeners.setdefault(event_name, []).append(key)

        self._cog_commands = commands
        self._cog_listeners = listeners
        self.qualified_name = qualified_name or name
        return self

class Cog(Generic[ClientT_D], metaclass=CogMeta):
    _cog_commands: list[Command[ClientT_D]]
    _cog_listeners: dict[str, list[str]]
    qualified_name: str

    def cog_load(self) -> None:
        """A special method that is called when the cog gets loaded."""
        pass

    def cog_unload(self) -> None:
        """A special method that is called when the cog gets removed."""
        pass

    def _inject(self, client: ClientT_D) -> None:
        client.cogs[self.qualified_name] = self

        for command in self._cog_commands:
            command.cog = self

            if command.parent is None:
                client.add_command(command)

        for key, listeners in self._cog_listeners.items():
            for listener_name in listeners:
                client.listeners.setdefault(key, []).append(getattr(self, listener_name))

        self.cog_load()

    def _uninject(self, client: ClientT_D) -> None:
        for name, command in client.all_commands.copy().items():
            if command in self._cog_commands:
                del client.all_commands[name]

        for key, listeners in self._cog_listeners.items():
            for listener_name in listeners:
                client.listeners[key].remove(getattr(self, listener_name))

        self.cog_unload()

    @property
    def commands(self) -> list[Command[ClientT_D]]:
        return self._cog_commands

    @staticmethod
    def listen(name: str | None = None) -> Callable[[Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]]:
        def inner(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]:
            if not func.__name__.startswith("on_"):
                raise RevoltError("event name must start with `on_`")

            setattr(func, "__listener_name", name or func.__name__[3:])
            return func

        return inner
