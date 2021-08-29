from __future__ import annotations

from typing import TYPE_CHECKING

from .user import User

if TYPE_CHECKING:
    from .state import State
    from .types import Member as MemberPayload
    from .server import Server

def flattern_user(member: Member, user: User):
    for attr in user.__flattern_attributes__:
        setattr(member, attr, getattr(user, attr))

class Member(User):
    def __init__(self, data: MemberPayload, server: Server, state: State):
        user = state.get_user(data["_id"]["user"])
        assert user
        flattern_user(self, user)

        self._state = state
        self.id = data["_id"]["user"]
        self.nickname = data.get("nickname")
        self.roles = [server.get_role(role_id) for role_id in data.get("roles", [])]
        self.server = server
