from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .channel import Channel

class Category(TypedDict):
    id: str
    title: str
    channels: list[Channel]
