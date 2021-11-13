from typing import Any, Callable, Coroutine, TypeVar, Union

from .command import Command
from .context import Context
from .errors import NotBotOwner, NotServerOwner, ServerOnly

__all__ = ("check", "Check", "is_bot_owner", "is_server_owner")

Check = Callable[[Context], Union[Any, Coroutine[Any, Any, Any]]]

T = TypeVar("T", Callable[..., Any], Command)

def check(check: Check):
    """A decorator for adding command checks

    Parameters
    -----------
    check: Callable[[Context], Union[Any, Coroutine[Any, Any, Any]]]
        The function to be called, must take one parameter, context and optionally be a coroutine

    Returns
    --------
    Any
        The value denoating whether the check should pass or fail
    """
    def inner(func: T) -> T:
        if isinstance(func, Command):
            func.checks.append(check)
        else:
            checks = getattr(func, "_checks", [])
            checks.append(check)
            func._checks = checks

        return func

    return inner

def is_bot_owner():
    """A command check for limiting the command to only the bot's owner"""
    @check
    def inner(context: Context):
        if context.author.id == context.client.user.owner_id:
            return True

        raise NotBotOwner

    return inner

def is_server_owner():
    """A command check for limiting the command to only a server's owner"""
    @check
    def inner(context: Context):
        if not context.server:
            raise ServerOnly

        if context.author.id == context.server.owner_id:
            return True

        raise NotServerOwner

    return inner
