from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional

import revolt
from revolt.utils import copy_doc

if TYPE_CHECKING:
    from .context import Context


__all__ = (
    "Command",
    "command"
)

class Command:
    """Class for holding info about a command.
    
    Parameters
    -----------
    callback: Callable[..., Coroutine[Any, Any, Any]]
        The callback for the command
    name: :class:`str`
        The name of the command
    aliases: list[:class:`str`]
        The aliases of the command
    """
    __slots__ = ("callback", "name", "aliases", "_client")

    _client: revolt.Client

    def __init__(self, callback: Callable[..., Coroutine[Any, Any, Any]], name: str, aliases: list[str]):
        self.callback = callback
        self.name = name
        self.aliases = aliases

    async def invoke(self, context: Context, args: list[Any]) -> Any:
        """Runs the command and calls the error handler if the command errors.

        Parameters
        -----------
        context: :class:`Context`
            The context for the command
        args: list[:class:`str`]
            The arguments for the command
        """
        try:
            return await self.callback(self._client, context, *args)
        except Exception as err:
            return await self._error_handler(context, err)

    @copy_doc(invoke)
    def __call__(self, context: Context, args: list[Any]) -> Any:
        return self.invoke(context, args)

    def error(self, func: Callable[..., Coroutine[Any, Any, Any]]):
        """Sets the error handler for the command.
        
        Parameters
        -----------
        func: Callable[..., Coroutine[Any, Any, Any]]
            The function for the error handler

        Example
        --------
        .. code-block:: python3

            @mycommand.error
            async def mycommand_error(self, ctx, error):
                await ctx.send(str(error))

        """
        self._error_handler = func  # type: ignore
        return func

    @staticmethod
    async def _error_handler(ctx: Context, error: Exception):
        traceback.print_exception(type(error), error, error.__traceback__)

def command(*, name: Optional[str] = None, aliases: Optional[list[str]] = None, cls: type[Command] = Command):
    """Turns a function into a :class:`Command`.
    
    Parameters
    -----------
    name: Optional[:class:`str`]
        The name of the command, this defaults to the functions name
    aliases: Optional[list[:class:`str`]]
        The aliases of the command, defaults to no aliases
    
    Returns
    --------
    :class:`Command`
        The command
    """
    def inner(func: Callable[..., Coroutine[Any, Any, Any]]):
        return cls(func, name or func.__name__, aliases or [])
    
    return inner
