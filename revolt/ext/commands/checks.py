from typing import Callable, Coroutine, Any, TypeVar, Union
from .command import Command
from .context import Context

__all__ = ("check", "Check")

Check = Callable[[Context], Union[Any, Coroutine[Any, Any, Any]]]

T = TypeVar("T", Callable[..., Any], Command)

def check(check: Check):
    def inner(func: T) -> T:
        if isinstance(func, Command):
            func.checks.append(check)
        else:
            checks = getattr(func, "_checks", [])
            checks.append(check)
            func._checks = checks

        return func

    return inner
