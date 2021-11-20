from __future__ import annotations

from typing import Callable, Iterator, Optional, TypeVar, Union, overload

__all__ = ("flag_value", "Flags", "UserBadges")

F_T = TypeVar("F_T", bound="Flags")
F_V = TypeVar("F_V", bound="flag_value")


class flag_value:
    __slots__ = ("flag", "__doc__")

    def __init__(self, func: Callable[[], int]):
        self.flag = func()
        self.__doc__ = func.__doc__

    @overload
    def __get__(self: F_V, instance: None, owner: type[F_T]) -> F_V:
        ...

    @overload
    def __get__(self, instance: F_T, owner: type[F_T]) -> bool:
        ...

    def __get__(self: F_V, instance: Optional[F_T], owner: type[F_T]) -> Union[F_V, bool]:
        if instance is None:
            return self

        return instance._check_flag(self.flag)

    def __set__(self, instance: Flags, value: bool):
        instance._set_flag(self.flag, value)

class Flags:
    def __init__(self, **kwargs: bool):
        self.value = 0

        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def _from_value(cls: type[F_T], value: int) -> F_T:
        self = cls.__new__(cls)
        self.value = value
        return self

    def _check_flag(self, flag: int) -> bool:
        return (self.value & flag) == flag

    def _set_flag(self, flag: int, value: bool):
        if value:
            self.value |= flag
        else:
            self.value &= ~flag

    def __eq__(self: F_T, other: F_T) -> bool:
        return self.value == other.value

    def __ne__(self: F_T, other: F_T) -> bool:
        return not self.__eq__(other)

    def __or__(self: F_T, other: F_T) -> F_T:
        return self.__class__._from_value(self.value | other.value)

    def __and__(self: F_T, other: F_T) -> F_T:
        return self.__class__._from_value(self.value & other.value)

    def __invert__(self: F_T) -> F_T:
        return self.__class__._from_value(~self.value)

    def __add__(self: F_T, other: F_T) -> F_T:
        return self | other

    def __sub__(self: F_T, other: F_T) -> F_T:
        return self & ~other

    def __lt__(self: F_T, other: F_T) -> bool:
        return self.value < other.value

    def __gt__(self: F_T, other: F_T) -> bool:
        return self.value > other.value

    def __repr__(self):
        return f"<{self.__class__.__name__} value={self.value}>"

    def __iter__(self) -> Iterator[tuple[str, bool]]:
        for name, value in self.__class__.__dict__.items():
            if isinstance(value, flag_value):
                yield name, value.__get__(self, self.__class__)

    def __hash__(self) -> int:
        return hash(self.value)

class UserBadges(Flags):
    """Contains all user badges"""

    @flag_value
    def developer():
        """:class:`bool` The developer badge."""
        return 1 << 0

    @flag_value
    def translator():
        """:class:`bool` The translator badge."""
        return 1 << 1

    @flag_value
    def supporter():
        """:class:`bool` The supporter badge."""
        return 1 << 2

    @flag_value
    def responsible_disclosure():
        """:class:`bool` The responsible disclosure badge."""
        return 1 << 3

    @flag_value
    def founder():
        """:class:`bool` The founder badge."""
        return 1 << 4

    @flag_value
    def platform_moderation():
        """:class:`bool` The platform moderation badge."""
        return 1 << 5

    @flag_value
    def active_supporter():
        """:class:`bool` The active supporter badge."""
        return 1 << 6

    @flag_value
    def paw():
        """:class:`bool` The paw badge."""
        return 1 << 7

    @flag_value
    def early_adopter():
        """:class:`bool` The early adopter badge."""
        return 1 << 8

    @flag_value
    def reserved_relevant_joke_badge_1():
        """:class:`bool` The reserved relevant joke badge 1 badge."""
        return 1 << 9
