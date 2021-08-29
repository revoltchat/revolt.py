from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .state import State
    from .types import Role as RolePayload

class Role:
    def __init__(self, data: RolePayload, role_id: str, state: State):
        self.id = role_id
        self.name = data["name"]
        self.colour = data.get("colour")
        self.hoist = data.get("hoist", False)
        self.rank = data.get("rank", 0)
