from __future__ import annotations

from typing import TYPE_CHECKING

from .permissions import ServerPermissions

if TYPE_CHECKING:
    from .server import Server
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
    server: :class:`Server`
        The server the role belongs to
    permissions: :class:`ServerPermissions`
        The server permissions for the role
    """
    __slots__ = ("id", "name", "colour", "hoist", "rank", "state", "server", "permissions")
    
    def __init__(self, data: RolePayload, role_id: str, state: State, server: Server):
        self.state = state
        self.id = role_id
        self.name = data["name"]
        self.colour = data.get("colour")
        self.hoist = data.get("hoist", False)
        self.rank = data.get("rank", 0)
        self.server = server
        self.permissions = ServerPermissions(*data.get("permissions"))

    @property
    def color(self):
        return self.colour

    async def set_permissions(self, permissions: ServerPermissions) -> None:
        """Sets the permissions for a role in a server.
        Parameters
        -----------
        permissions: :class:`ServerPermissions`
            The new permissions for the role
        """
        await self.state.http.set_role_permissions(self.server.id, self.id, *permissions.value)
