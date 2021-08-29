from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import State
    from .types import Member as MemberPayload
    from .server import Server

class Member:
    def __init__(self, data: MemberPayload, server: Server, state: State):
        self._state = state
        self.id = data["_id"]
        self.nickname = data.get("nickname")
        self.roles = [server.get_role(role_id) for role_id in data.get("roles", [])]

        self.server = server
