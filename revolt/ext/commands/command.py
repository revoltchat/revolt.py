from __future__ import annotations

import inspect
import traceback
from contextlib import suppress
from typing import (TYPE_CHECKING, Annotated, Any, Callable, Coroutine,
                    Literal, Optional, Union, cast, get_args, get_origin)

import revolt
from revolt.utils import copy_doc, maybe_coroutine

from .errors import InvalidLiteralArgument, UnionConverterError
from .utils import evaluate_parameters

if TYPE_CHECKING:
    from .context import Context
    from .checks import Check
    from .group import Group
    from .cog import Cog

__all__ = (
    "Command",
    "command"
)

NoneType = type(None)


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
    parent: Optional[:class:`Group`]
        The parent of the command if this command is a subcommand
    cog: Optional[:class:`Cog`]
        The cog the command is apart of.
    usage: Optional[:class:`str`]
        The usage string for the command
    """
    __slots__ = ("callback", "name", "aliases", "signature", "checks", "parent", "_error_handler", "cog", "description", "usage", "parameters")

    def __init__(self, callback: Callable[..., Coroutine[Any, Any, Any]], name: str, aliases: list[str], usage: Optional[str] = None):
        self.callback = callback
        self.name = name
        self.aliases = aliases
        self.usage = usage
        self.signature = inspect.signature(self.callback)
        self.parameters = evaluate_parameters(self.signature.parameters.values(), getattr(callback, "__globals__", {}))
        self.checks: list[Check] = getattr(callback, "_checks", [])
        self.parent: Optional[Group] = None
        self.cog: Optional[Cog] = None
        self._error_handler: Callable[[Any, Context, Exception], Coroutine[Any, Any, Any]] = type(self)._default_error_handler
        self.description = callback.__doc__

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
            return await self.callback(self.cog or context.client, context, *args, **kwargs)
        except Exception as err:
            return await self._error_handler(self.cog or context.client, context, err)

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
        self._error_handler = func
        return func

    async def _default_error_handler(self, ctx: Context, error: Exception):
        traceback.print_exception(type(error), error, error.__traceback__)

    @classmethod
    async def handle_origin(cls, context: Context, origin: Any, annotation: Any, arg: str) -> Any:
        if origin is Union:
            for converter in get_args(annotation):
                try:
                    return await cls.convert_argument(arg, converter, context)
                except:
                    if converter is NoneType:
                        context.view.undo()
                        return None

            raise UnionConverterError(arg)

        elif origin is Annotated:
            annotated_args = get_args(annotation)

            if origin := get_origin(annotated_args[0]):
                return await cls.handle_origin(context, origin, annotated_args[1], arg)
            else:
                return await cls.convert_argument(arg, annotated_args[1], context)

        elif origin is Literal:
            if arg in get_args(annotation):
                return arg
            else:
                raise InvalidLiteralArgument(arg)

    @classmethod
    async def convert_argument(cls, arg: str, annotation: Any, context: Context) -> Any:
        if annotation is not inspect.Signature.empty:
            if annotation is str:  # no converting is needed - its already a string
                return arg

            if origin := get_origin(annotation):
                return await cls.handle_origin(context, origin, annotation, arg)
            else:
                return await maybe_coroutine(annotation, arg, context)
        else:
            return arg

    async def parse_arguments(self, context: Context):
        # please pr if you can think of a better way to do this

        for parameter in self.parameters[2:]:
            if parameter.kind == parameter.KEYWORD_ONLY:
                try:
                    arg = await self.convert_argument(context.view.get_rest(), parameter.annotation, context)
                except StopIteration:
                    if parameter.default is not parameter.empty:
                        arg = parameter.default
                    else:
                        raise

                context.kwargs[parameter.name] = arg

            elif parameter.kind == parameter.VAR_POSITIONAL:
                with suppress(StopIteration):
                    while True:
                        context.args.append(await self.convert_argument(context.view.get_next_word(), parameter.annotation, context))

            elif parameter.kind == parameter.POSITIONAL_OR_KEYWORD:
                try:
                    rest = context.view.get_next_word()
                    arg = await self.convert_argument(rest, parameter.annotation, context)
                except StopIteration:
                    if parameter.default is not parameter.empty:
                        arg = parameter.default
                    else:
                        raise

                context.args.append(arg)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name=\"{self.name}\">"

    @property
    def short_description(self) -> Optional[str]:
        """Returns the first line of the description or None if there is no description."""
        if self.description:
            return self.description.split("\n")[0]

    def get_usage(self) -> str:
        """Returns the usage string for the command."""
        if self.usage:
            return self.usage

        parents = []

        if self.parent:
            parent = self.parent

            while parent:
                parents.append(parent.name)
                parent = parent.parent

        parameters = []

        for parameter in self.parameters[2:]:
            if parameter.kind == parameter.POSITIONAL_OR_KEYWORD:
                if parameter.default is not parameter.empty:
                    parameters.append(f"[{parameter.name}]")
                else:
                    parameters.append(f"<{parameter.name}>")
            elif parameter.kind == parameter.KEYWORD_ONLY:
                if parameter.default is not parameter.empty:
                    parameters.append(f"[{parameter.name}]")
                else:
                    parameters.append(f"<{parameter.name}...>")
            elif parameter.kind == parameter.VAR_POSITIONAL:
                parameters.append(f"[{parameter.name}...]")

        return f"{' '.join(parents[::-1])} {self.name} {' '.join(parameters)}"

def command(*, name: Optional[str] = None, aliases: Optional[list[str]] = None, cls: type[Command] = Command, usage: Optional[str] = None):
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
        return cls(func, name or func.__name__, aliases or [], usage)

    return inner
