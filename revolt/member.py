from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .asset import Asset
from .user import User

if TYPE_CHECKING:
    from .server import Server
    from .state import State
    from .types import File
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
    guild_avatar: Optional[:class:`Asset`]
        The member's guild avatar if any
    """
    __slots__ = ("_state", "nickname", "roles", "server", "guild_avatar")
    
    def __init__(self, data: MemberPayload, server: Server, state: State):
        user = state.get_user(data["_id"]["user"])
        flattern_user(self, user)

        self._state = state
        self.nickname = data.get("nickname")

        if avatar := data.get("avatar"):
            self.guild_avatar = Asset(avatar, state)
        else:
            self.guild_avatar = None

        roles = [server.get_role(role_id) for role_id in data.get("roles", [])]
        self.roles = sorted(roles, key=lambda role: role.rank, reverse=True)

        self.server = server

    @property
    def avatar(self) -> Optional[Asset]:
        """Optional[:class:`Asset`] The avatar the member is displaying, this includes guild avatars and masqueraded avatar"""
        return self.masquerade_avatar or self.guild_avatar or self.original_avatar

    def _update(self, *, nickname: Optional[str] = None, avatar: Optional[File] = None, roles: Optional[list[str]] = None):
        if nickname:
            self.nickname = nickname

        if avatar:
            self.guild_avatar = Asset(avatar, self.state)

        if roles:
            member_roles = [self.server.get_role(role_id) for role_id in roles]
            self.roles = sorted(member_roles, key=lambda role: role.rank, reverse=True)
