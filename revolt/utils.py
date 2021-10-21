from typing import Callable, TypeVar

__all__ = ("Missing", "copy_doc")

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
