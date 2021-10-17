from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .user import User

if TYPE_CHECKING:
    from .server import Server
    from .state import State
    from .types import Member as MemberPayload


__all__ = ("Member",)

def flattern_user(member: Member, user: User):
    for attr in user.__flattern_attributes__:
        setattr(member, attr, getattr(user, attr))

class Member(User):
    """Represents a member of a server, subclasses :class:`User`
    
    Attributes
    -----------
    nickname: Optional[:class:`str`]
        The nickname of the member if any
    roles: list[:class:`Role`]
        The roles of the member, ordered by the role's rank in decending order
    server: :class:`Server`
        The server the member belongs to
    """
    __slots__ = ("_state", "nickname", "roles", "server")
    
    def __init__(self, data: MemberPayload, server: Server, state: State):
        user = state.get_user(data["_id"]["user"])
        assert user
        flattern_user(self, user)

        self._state = state
        self.nickname = data.get("nickname")
        roles = []

        for role in (server.get_role(role_id) for role_id in data.get("roles", [])):
            if role:
                roles.append(role)

        self.roles = sorted(roles, key=lambda role: role.rank, reverse=True)
        
        self.server = server

    @property
    def owner(self) -> Optional[User]:
        owner_id = self.owner_id

        if not owner_id:
            return

        return self.state.get_user(owner_id)
