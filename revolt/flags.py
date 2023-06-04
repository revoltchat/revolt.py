from __future__ import annotations

from typing import Callable, Iterator, Optional, Union, overload

from typing_extensions import Self

__all__ = ("Flag", "Flags", "UserBadges")


class Flag:
    __slots__ = ("flag", "__doc__")

    def __init__(self, func: Callable[[], int]):
        self.flag: int = func()
        self.__doc__: str | None = func.__doc__

    @overload
    def __get__(self: Self, instance: None, owner: type[Flags]) -> Self:
        ...

    @overload
    def __get__(self, instance: Flags, owner: type[Flags]) -> bool:
        ...

    def __get__(self: Self, instance: Optional[Flags], owner: type[Flags]) -> Union[Self, bool]:
        if instance is None:
            return self

        return instance._check_flag(self.flag)

    def __set__(self, instance: Flags, value: bool) -> None:
        instance._set_flag(self.flag, value)

class Flags:
    FLAG_NAMES: list[str]

    def __init_subclass__(cls) -> None:
        cls.FLAG_NAMES = []

        for name in dir(cls):
            value = getattr(cls, name)

            if isinstance(value, Flag):
                cls.FLAG_NAMES.append(name)

    def __init__(self, value: int = 0, **flags: bool):
        self.value = value

        for k, v in flags.items():
            setattr(self, k, v)

    @classmethod
    def _from_value(cls, value: int) -> Self:
        self = cls.__new__(cls)
        self.value = value
        return self

    def _check_flag(self, flag: int) -> bool:
        return (self.value & flag) == flag

    def _set_flag(self, flag: int, value: bool) -> None:
        if value:
            self.value |= flag
        else:
            self.value &= ~flag

    def __eq__(self, other: Self) -> bool:
        return self.value == other.value

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __or__(self, other: Self) -> Self:
        return self.__class__._from_value(self.value | other.value)

    def __and__(self, other: Self) -> Self:
        return self.__class__._from_value(self.value & other.value)

    def __invert__(self) -> Self:
        return self.__class__._from_value(~self.value)

    def __add__(self, other: Self) -> Self:
        return self | other

    def __sub__(self, other: Self) -> Self:
        return self & ~other

    def __lt__(self, other: Self) -> bool:
        return self.value < other.value

    def __gt__(self, other: Self) -> bool:
        return self.value > other.value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} value={self.value}>"

    def __iter__(self) -> Iterator[tuple[str, bool]]:
        for name, value in self.__class__.__dict__.items():
            if isinstance(value, Flag):
                yield name, self._check_flag(value.flag)

    def __hash__(self) -> int:
        return hash(self.value)

class UserBadges(Flags):
    """Contains all user badges"""

    @Flag
    def developer():
        """:class:`bool` The developer badge."""
        return 1 << 0

    @Flag
    def translator():
        """:class:`bool` The translator badge."""
        return 1 << 1

    @Flag
    def supporter():
        """:class:`bool` The supporter badge."""
        return 1 << 2

    @Flag
    def responsible_disclosure():
        """:class:`bool` The responsible disclosure badge."""
        return 1 << 3

    @Flag
    def founder():
        """:class:`bool` The founder badge."""
        return 1 << 4

    @Flag
    def platform_moderation():
        """:class:`bool` The platform moderation badge."""
        return 1 << 5

    @Flag
    def active_supporter():
        """:class:`bool` The active supporter badge."""
        return 1 << 6

    @Flag
    def paw():
        """:class:`bool` The paw badge."""
        return 1 << 7

    @Flag
    def early_adopter():
        """:class:`bool` The early adopter badge."""
        return 1 << 8

    @Flag
    def reserved_relevant_joke_badge_1():
        """:class:`bool` The reserved relevant joke badge 1 badge."""
        return 1 << 9
