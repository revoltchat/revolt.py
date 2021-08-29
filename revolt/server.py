from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .types import Server as ServerPayload
    from .state import State
    from .member import Member
    from .role import Role
    from .channel import Channel

class Server:
    def __init__(self, data: ServerPayload, state: State):
        self.state = state
        self.id = data["_id"]
        
        self._members: dict[str, Member] = {}
        self._roles: dict[str, Role] = {}
        self._channels: dict[str, Channel] = {}

    def get_role(self, role_id: str, /) -> Optional[Role]:
        return self._roles.get(role_id)

    def get_member(self, member_id: str, /) -> Optional[Member]:
        return self._members.get(member_id)
