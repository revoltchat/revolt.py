from typing import TypedDict

__all__ = ("Category",)

class Category(TypedDict):
    id: str
    title: str
    channels: list[str]
