from typing import Callable, Coroutine, Any, Union, TYPE_CHECKING
from .command import Command
from .context import Context

__all__ = ("check", "Check")

Check = Callable[[Context], Union[bool, Coroutine[Any, Any, bool]]]

def check(check: Check):
    def inner(func: Union[Callable[..., Any], Command]):
        if isinstance(func, Command):
            func.checks.append(check)
        else:
            checks = getattr(func, "_checks", [])
            checks.append(check)
            func._checks = checks

        return func

    return inner
