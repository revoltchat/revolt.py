from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import State
    from .types import Role as RolePayload


__all__ = ("Role",)

class Role:
    """Represents a role
    
    Attributes
    -----------
    id: :class:`str`
        The id of the role
    name: :class:`str`
        The name of the role
    colour: :class:`str`
        The colour of the role
    hoist: :class:`bool`
        Whether members with the role will display seperate from everyone else
    rank: :class:`int`
        The position of the role in the role heirarchy
    """
    __slots__ = ("id", "name", "colour", "hoist", "rank")
    
    def __init__(self, data: RolePayload, role_id: str, state: State):
        self.id = role_id
        self.name = data["name"]
        self.colour = data.get("colour")
        self.hoist = data.get("hoist", False)
        self.rank = data.get("rank", 0)

    @property
    def color(self):
        return self.colour