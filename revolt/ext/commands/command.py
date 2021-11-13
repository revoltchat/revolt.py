from __future__ import annotations

import inspect
import traceback
from contextlib import suppress
from typing import (TYPE_CHECKING, Annotated, Any, Callable, Coroutine,
                    Literal, Optional, Union, get_args, get_origin)

import revolt
from revolt.utils import copy_doc, maybe_coroutine

from .errors import InvalidLiteralArgument

if TYPE_CHECKING:
    from .checks import Check
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
    __slots__ = ("callback", "name", "aliases", "_client", "signature", "checks")

    _client: revolt.Client

    def __init__(self, callback: Callable[..., Coroutine[Any, Any, Any]], name: str, aliases: list[str]):
        self.callback = callback
        self.name = name
        self.aliases = aliases
        self.signature = inspect.signature(self.callback)
        self.checks: list[Check] = getattr(callback, "_checks", [])

    async def invoke(self, context: Context, *args, **kwargs) -> Any:
        """Runs the command and calls the error handler if the command errors.

        Parameters
        -----------
        context: :class:`Context`
            The context for the command
        args: list[:class:`str`]
            The arguments for the command
        """
        try:
            return await self.callback(self._client, context, *args, **kwargs)
        except Exception as err:
            return await self._error_handler(context, err)

    @copy_doc(invoke)
    def __call__(self, context: Context, *args, **kwargs) -> Any:
        return self.invoke(context, *args, **kwargs)

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

    @staticmethod
    def extract_type(t):
        if origin := get_origin(t):
            if origin is Annotated:
                return get_args(t)[1]

        return t

    @classmethod
    async def convert_argument(cls, arg: str, parameter: inspect.Parameter, context: Context):
        if annot := parameter.annotation:
            if annot is str:  # no converting is needed - its already a string
                return arg

            if origin := get_origin(annot):
                if origin is Union:
                    for converter in get_args(annot):

                        try:
                            return await maybe_coroutine(converter, arg, context)
                        except:
                            if converter is None:
                                context.view.undo()
                                return None

                elif origin is Annotated:
                    converter: Callable[[str, Context], Any] = get_args(annot)[1]  # the typehint affects the other if statement somehow
                    return await maybe_coroutine(converter, arg, context)

                elif origin is Literal:
                    if arg in get_args(annot):
                        return arg
                    else:
                        raise InvalidLiteralArgument(arg)
            else:
                annot: Callable[..., Any]
                return await maybe_coroutine(annot, arg, context)
        else:
            return arg

    async def parse_arguments(self, context: Context):
        for name, parameter in list(self.signature.parameters.items())[2:]:
            if parameter.kind == parameter.KEYWORD_ONLY:
                context.kwargs[name] = await self.convert_argument(context.view.get_rest(), parameter, context)

            elif parameter.kind == parameter.VAR_POSITIONAL:
                with suppress(StopIteration):
                    while True:
                        context.args.append(await self.convert_argument(context.view.get_next_word(), parameter, context))

            elif parameter.kind == parameter.POSITIONAL_OR_KEYWORD:
                context.args.append(await self.convert_argument(context.view.get_next_word(), parameter, context))

    def __repr__(self) -> str:
        return f"<Command name=\"{self.name}\">"

def command(*, name: Optional[str] = None, aliases: Optional[list[str]] = None, cls: type[Command] = Command):
    """A decorator that turns a function into a :class:`Command`.

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
        return cls(func, name or func.__name__, aliases or [])

    return inner
