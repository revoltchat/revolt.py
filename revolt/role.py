from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from revolt.types import server

from .permissions import ChannelPermissions, ServerPermissions

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
    server_permissions: :class:`ServerPermissions`
        The server permissions for the role
    channel_permissions: :class:`ChannelPermissions`
        The channel permissions for the role
    """
    __slots__ = ("id", "name", "colour", "hoist", "rank", "state", "server", "server_permissions", "channel_permissions")

    def __init__(self, data: RolePayload, role_id: str, state: State, server: Server):
        self.state = state
        self.id = role_id
        self.name = data["name"]
        self.colour = data.get("colour")
        self.hoist = data.get("hoist", False)
        self.rank = data.get("rank", 0)
        self.server = server
        self.server_permissions = ServerPermissions._from_value(data["permissions"][0])
        self.channel_permissions = ChannelPermissions._from_value(data["permissions"][1])

    @property
    def color(self):
        return self.colour

    async def set_permissions(self, *, server_permissions: Optional[ServerPermissions] = None, channel_permissions: Optional[ChannelPermissions] = None) -> None:
        """Sets the permissions for a role in a server.
        Parameters
        -----------
        server_permissions: Optional[:class:`ServerPermissions`]
            The new server permissions for the role
        channel_permissions: Optional[:class:`ChannelPermissions`]
            The new channel permissions for the role
        """

        if not server_permissions and not channel_permissions:
            return

        server_value = (server_permissions or self.server_permissions).value
        channel_value = (channel_permissions or self.channel_permissions).value

        await self.state.http.set_role_permissions(self.server.id, self.id, server_value, channel_value)

    def _update(self, *, name: Optional[str] = None, colour: Optional[str] = None, hoist: Optional[bool] = None, rank: Optional[int] = None):
        if name:
            self.name = name

        if colour:
            self.colour = colour

        if hoist:
            self.hoist = hoist

        if rank:
            self.rank = rank
