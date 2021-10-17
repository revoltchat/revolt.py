from __future__ import annotations

import traceback
import revolt
from typing import Callable, Coroutine, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .context import Context


__all__ = (
    "Command",
    "command"
)

class Command:
    _client: revolt.Client

    def __init__(self, callback: Callable[..., Coroutine[Any, Any, Any]], name: str, aliases: list[str]):
        self.callback = callback
        self.name = name
        self.aliases = aliases

    async def invoke(self, context: Context, args: list[str]) -> Any:
        try:
            return await self.callback(self._client, context, *args)
        except Exception as err:
            return await self._error_handler(context, err)

    def error(self, func: Callable[..., Coroutine[Any, Any, Any]]):
        self._error_handler = func  # type: ignore
        return func

    @staticmethod
    async def _error_handler(ctx: Context, error: Exception):
        traceback.print_exception(type(error), error, error.__traceback__)


def command(*, name: Optional[str] = None, aliases: Optional[list[str]] = None):
    def inner(func: Callable[..., Coroutine[Any, Any, Any]]):
        return Command(func, name or func.__name__, aliases or [])
    
    return inner

