import inspect
from operator import attrgetter
from typing import Any, Callable, Coroutine, Iterable, TypeVar, Union
from contextlib import asynccontextmanager
from typing_extensions import ParamSpec
from aiohttp import ClientSession

__all__ = ("Missing", "copy_doc", "maybe_coroutine", "get", "client_session")

class _Missing:
    def __repr__(self):
        return "<Missing>"

Missing = _Missing()

T = TypeVar("T")

def copy_doc(from_t: T) -> Callable[[T], T]:
    def inner(to_t: T) -> T:
        to_t.__doc__ = from_t.__doc__
        return to_t

    return inner

R_T = TypeVar("R_T")
P = ParamSpec("P")

# it is impossible to type this function correctly for a couple reasons:
# 1. isawaitable does not narrow while keeping typevars - there is an open PR for this (typeshed#5658) but it cannot be merged because mypy does not support the feature fully
# 2. typeguard does not narrow for the negative case which is dumb in my opinion, so `value` would stay being a union even after the if statement (PEP 647 - "The type is not narrowed in the negative case")

async def maybe_coroutine(func: Callable[P, Union[R_T, Coroutine[Any, Any, R_T]]], *args: P.args, **kwargs: P.kwargs) -> R_T:
    value = func(*args, **kwargs)

    if inspect.isawaitable(value):
        value = await value

    return value  # type: ignore


def get(iterable: Iterable[T], **attrs: Any) -> T:
    """A convenience function to help get a value from an iterable with a specific attribute

    Examples
    ---------

    .. code-block:: python
        :emphasize-lines: 3

        from revolt import utils

        channel = utils.get(server.channels, name="General")
        await channel.send("Hello general chat.")

    Parameters
    -----------
    iterable: Iterable
        The values to search though
    **attrs: Any
        The attributes to check

    Returns
    --------
    Any
        The value from the iterable with the met attributes

    Raises
    -------
    LookupError
        Raises when none of the values in the iterable matches the attributes

    """
    converted = [(attrgetter(attr.replace('__', '.')), value) for attr, value in attrs.items()]

    for elem in iterable:
        if all(pred(elem) == value for pred, value in converted):
            return elem

    raise LookupError


@asynccontextmanager
async def client_session():
    """A context manager that creates a new aiohttp.ClientSession() and closes it when exiting the context.

    Examples
    ---------

    .. code-block:: python
        :emphasize-lines: 3

        async def main():
            async with client_session() as session:
                client = revolt.Client(session, "TOKEN")
                await client.start()

        asyncio.run(main())
    """
    session = ClientSession()

    try:
        yield session
    finally:
        await session.close()
