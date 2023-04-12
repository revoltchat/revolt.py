from __future__ import annotations

from typing import Any, Callable, Coroutine, TypeVar, Union, cast

import revolt

from .command import Command
from .context import Context
from .errors import (MissingPermissionsError, NotBotOwner, NotServerOwner,
                     ServerOnly)
from .utils import ClientT

__all__ = ("check", "Check", "is_bot_owner", "is_server_owner", "has_permissions", "has_channel_permissions")

T = TypeVar("T", Callable[..., Any], Command)

Check = Callable[[Context[ClientT]], Union[Any, Coroutine[Any, Any, Any]]]

def check(check: Check[ClientT]):
    """A decorator for adding command checks

    Parameters
    -----------
    check: Callable[[Context], Union[Any, Coroutine[Any, Any, Any]]]
        The function to be called, must take one parameter, context and optionally be a coroutine, the return value denoating whether the check should pass or fail
    """
    def inner(func: T) -> T:
        if isinstance(func, Command):
            command = cast(Command[ClientT], func)  # cant verify generic at runtime so must cast
            command.checks.append(check)
        else:
            checks = getattr(func, "_checks", [])
            checks.append(check)
            func._checks = checks  # type: ignore

        return func

    return inner

def is_bot_owner():
    """A command check for limiting the command to only the bot's owner"""
    @check
    def inner(context: Context[ClientT]):
        if context.author.id == context.client.user.owner_id:
            return True

        raise NotBotOwner

    return inner

def is_server_owner():
    """A command check for limiting the command to only a server's owner"""
    @check
    def inner(context: Context[ClientT]):
        if not context.server:
            raise ServerOnly

        if context.author.id == context.server.owner_id:
            return True

        raise NotServerOwner

    return inner

def has_permissions(**permissions: bool):
    @check
    def inner(context: Context[ClientT]):
        author = context.author

        if not author.has_permissions(**permissions):
            raise MissingPermissionsError

    return inner

def has_channel_permissions(**permissions: bool):
    @check
    def inner(context: Context[ClientT]):
        author = context.author

        if isinstance(author, revolt.User):
            raise MissingPermissionsError

        if not author.has_channel_permissions(context.channel, **permissions):
            raise MissingPermissionsError

    return inner
