from __future__ import annotations

from typing import TYPE_CHECKING

from .utils import Ulid

if TYPE_CHECKING:
    from .channel import Channel
    from .state import State
    from .types import Category as CategoryPayload

__all__ = ("Category",)

class Category(Ulid):
    """Represents a category in a server that stores channels.

    Attributes
    -----------
    name: :class:`str`
        The name of the category
    id: :class:`str`
        The id of the category
    channel_ids: list[:class:`str`]
        The ids of channels that are inside the category
    """

    def __init__(self, data: CategoryPayload, state: State):
        self.state: State = state
        self.name: str = data["title"]
        self.id: str = data["id"]
        self.channel_ids: list[str] = data["channels"]

    @property
    def channels(self) -> list[Channel]:
        """Returns a list of channels that the category contains"""
        return [self.state.get_channel(channel_id) for channel_id in self.channel_ids]
