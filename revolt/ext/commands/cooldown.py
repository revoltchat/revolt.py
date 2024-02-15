from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Callable, Coroutine, TypeVar, cast

from .errors import ServerOnly

if TYPE_CHECKING:
    from enum import Enum

    from .context import Context
    from .utils import ClientT_Co_D, ClientT_Co
else:
    from aenum import Enum

__all__ = ("Cooldown", "CooldownMapping", "BucketType", "cooldown")

T = TypeVar("T")

class Cooldown:
    """Represent a single cooldown for a single key

    Parameters
    -----------
    rate: :class:`int`
        How many times it can be used
    per: :class:`int`
        How long the window is before the ratelimit resets
    """

    def __init__(self, rate: int, per: int):
        self.rate: int = rate
        self.per: int = per
        self.window: float = 0.0
        self.tokens: int = rate
        self.last: float = 0.0

    def get_tokens(self, current: float | None) -> int:
        current = current or time.time()

        if current > (self.window + self.per):
            return self.rate
        else:
            return self.tokens

    def update_cooldown(self) -> float | None:
        current = time.time()

        self.last = current

        self.tokens = self.get_tokens(current)

        if self.tokens == 0:
            return self.per - (current - self.window)

        self.tokens -= 1

        if self.tokens == 0:
            self.window = current

        return None

class CooldownMapping:
    """Holds all cooldowns for every key"""
    def __init__(self, rate: int, per: int):
        self.rate = rate
        self.per = per
        self.cache: dict[str, Cooldown] = {}

    def verify_cache(self) -> None:
        current = time.time()
        self.cache = {k: v for k, v in self.cache.items() if current < (v.last + v.per)}

    def get_bucket(self, key: str) -> Cooldown:
        self.verify_cache()

        if not (rl := self.cache.get(key)):
            self.cache[key] = rl = Cooldown(self.rate, self.per)

        return rl

class BucketType(Enum):
    default = 0
    user = 1
    server = 2
    channel = 3
    member = 4

    def resolve(self, context: Context[ClientT_Co_D]) -> str:
        if self == BucketType.default:
            return f"{context.author.id}{context.channel.id}"

        elif self == BucketType.user:
            return context.author.id

        elif self == BucketType.server:
            if id := context.server_id:
                return id

            raise ServerOnly

        elif self == BucketType.channel:
            return context.channel.id

        else:  # BucketType.member
            if server_id := context.server_id:
                return f"{context.author.id}{server_id}"

            raise ServerOnly

def cooldown(rate: int, per: int, *, bucket: BucketType | Callable[[Context[ClientT_Co]], Coroutine[Any, Any, str]] = BucketType.default) -> Callable[[T], T]:
    """Adds a cooldown to a command

    Parameters
    -----------
    rate: :class:`int`
        How many times it can be used
    per: :class:`int`
        How long the window is before the ratelimit resets
    bucket: Optional[Union[:class:`BucketType`, Callable[[Context], str]]]
        Controls how the key is generated for the cooldowns

    Examples
    --------
    .. code-block:: python
        @commands.command()
        @commands.cooldown(1, 5)
        async def ping(self, ctx: Context):
            await ctx.send("Pong")
    """
    def inner(func: T) -> T:
        from .command import Command

        if isinstance(func, Command):
            command = cast(Command[ClientT_Co], func)  # cant verify generic at runtime so must cast
            command.cooldown = CooldownMapping(rate, per)
            command.cooldown_bucket = bucket
        else:
            func._cooldown = CooldownMapping(rate, per)  # type: ignore
            func._bucket = bucket  # type: ignore

        return func

    return inner