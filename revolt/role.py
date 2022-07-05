from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .permissions import Permissions, PermissionsOverwrite
from .utils import Missing

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
    colour: Optional[:class:`str`]
        The colour of the role
    hoist: :class:`bool`
        Whether members with the role will display seperate from everyone else
    rank: :class:`int`
        The position of the role in the role heirarchy
    server: :class:`Server`
        The server the role belongs to
    server_permissions: :class:`ServerPermissions`
        The server permissions for the role
    channel_permissions: :class:`ChannelPermissions`
        The channel permissions for the role
    """
    __slots__ = ("id", "name", "colour", "hoist", "rank", "state", "server", "permissions")

    def __init__(self, data: RolePayload, role_id: str, server: Server, state: State):
        self.state = state
        self.id = role_id
        self.name = data["name"]
        self.colour = None
        self.hoist = False
        self.rank = 0
        self.server = server
        self.permissions = PermissionsOverwrite._from_overwrite(data.get("permissions", {"a": 0, "d": 0}))

    @property
    def color(self):
        return self.colour

    async def set_permissions_overwrite(self, *, permissions: PermissionsOverwrite) -> None:
        """Sets the permissions for a role in a server.
        Parameters
        -----------
        server_permissions: Optional[:class:`ServerPermissions`]
            The new server permissions for the role
        channel_permissions: Optional[:class:`ChannelPermissions`]
            The new channel permissions for the role
        """
        allow, deny = permissions.to_pair()
        await self.state.http.set_server_role_permissions(self.server.id, self.id, allow.value, deny.value)

    def _update(self, *, name: Optional[str] = None, colour: Optional[str] = None, hoist: Optional[bool] = None, rank: Optional[int] = None):
        if name:
            self.name = name

        if colour:
            self.colour = colour

        if hoist:
            self.hoist = hoist

        if rank:
            self.rank = rank

    async def delete(self):
        """Deletes the role"""
        await self.state.http.delete_role(self.server.id, self.id)

    async def edit(self, **kwargs):
        """Edits the role

        Parameters
        -----------
        """
        if kwargs.get("colour", Missing) is None:
            remove = "Colour"
        else:
            remove = None

        await self.state.http.edit_role(self.server.id, self.id, remove, kwargs)
