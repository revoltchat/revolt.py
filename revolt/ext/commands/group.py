from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Callable, Coroutine, Any

from .command import Command

if TYPE_CHECKING:
    from .context import Context

__all__ = (
    "Group",
    "group"
)


class Group(Command):
    """Class for holding info about a group command.

    Parameters
    -----------
    callback: Callable[..., Coroutine[Any, Any, Any]]
        The callback for the group command
    name: :class:`str`
        The name of the command
    aliases: list[:class:`str`]
        The aliases of the group command
    subcommands: dict[:class:`str`, :class:`Command`]
        The group's subcommands.
    """

    __slots__ = ("subcommands",)

    def __init__(self, callback: Callable[..., Coroutine[Any, Any, Any]], name: str, aliases: list[str]):
        self.subcommands: dict[str, Command] = {}
        super().__init__(callback, name, aliases)

    def command(self, *, name: Optional[str] = None, aliases: Optional[list[str]] = None, cls: type[Command] = Command):
        """A decorator that turns a function into a :class:`Command` and registers the command as a subcommand.

        Parameters
        -----------
        name: Optional[:class:`str`]
            The name of the command, this defaults to the functions name
        aliases: Optional[list[:class:`str`]]
            The aliases of the command, defaults to no aliases
        cls: type[:class:`Command`]
            The class used for creating the command, this defaults to :class:`Command` but can be used to use a custom command subclass

        Returns
        --------
        Callable[Callable[..., Coroutine], :class:`Command`]
            A function that takes the command callback and returns a :class:`Command`
        """
        def inner(func: Callable[..., Coroutine[Any, Any, Any]]):
            command = cls(func, name or func.__name__, aliases or [])
            command.parent = self
            self.subcommands[command.name] = command
            return command

        return inner

    def group(self, *, name: Optional[str] = None, aliases: Optional[list[str]] = None, cls: Optional[type["Group"]] = None):
        """A decorator that turns a function into a :class:`Group` and registers the command as a subcommand

        Parameters
        -----------
        name: Optional[:class:`str`]
            The name of the group command, this defaults to the functions name
        aliases: Optional[list[:class:`str`]]
            The aliases of the group command, defaults to no aliases
        cls: type[:class:`Group`]
            The class used for creating the command, this defaults to :class:`Group` but can be used to use a custom group subclass

        Returns
        --------
        Callable[Callable[..., Coroutine], :class:`Group`]
            A function that takes the command callback and returns a :class:`Group`
        """
        cls = cls or type(self)

        def inner(func: Callable[..., Coroutine[Any, Any, Any]]):
            command = cls(func, name or func.__name__, aliases or [])
            command.parent = self
            self.subcommands[command.name] = command
            return command

        return inner

    def __repr__(self) -> str:
        return f"<Group name=\"{self.name}\">"

    @property
    def commands(self) -> list[Command]:
        return list(self.subcommands.values())

def group(*, name: Optional[str] = None, aliases: Optional[list[str]] = None, cls: type[Group] = Group):
    """A decorator that turns a function into a :class:`Group`

    Parameters
    -----------
    name: Optional[:class:`str`]
        The name of the group command, this defaults to the functions name
    aliases: Optional[list[:class:`str`]]
        The aliases of the group command, defaults to no aliases
    cls: type[:class:`Group`]
        The class used for creating the command, this defaults to :class:`Group` but can be used to use a custom group subclass

    Returns
    --------
    Callable[Callable[..., Coroutine], :class:`Group`]
        A function that takes the command callback and returns a :class:`Group`
    """

    def inner(func: Callable[..., Coroutine[Any, Any, Any]]):
        return cls(func, name or func.__name__, aliases or [])

    return inner
