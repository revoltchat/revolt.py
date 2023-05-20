from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .permissions import Overwrite, PermissionsOverwrite
from .utils import Missing, Ulid

if TYPE_CHECKING:
    from .server import Server
    from .state import State
    from .types import Role as RolePayload


__all__ = ("Role",)

class Role(Ulid):
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
    __slots__: tuple[str, ...] = ("id", "name", "colour", "hoist", "rank", "state", "server", "permissions")

    def __init__(self, data: RolePayload, role_id: str, server: Server, state: State):
        self.state: State = state
        self.id: str = role_id
        self.name: str = data["name"]
        self.colour: str | None = data.get("colour", None)
        self.hoist: bool = data.get("hoist", False)
        self.rank: int = data["rank"]
        self.server: Server = server
        self.permissions: PermissionsOverwrite = PermissionsOverwrite._from_overwrite(data.get("permissions", {"a": 0, "d": 0}))

    @property
    def color(self) -> str | None:
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

    def _update(self, *, name: Optional[str] = None, colour: Optional[str] = None, hoist: Optional[bool] = None, rank: Optional[int] = None, permissions: Optional[Overwrite] = None) -> None:
        if name is not None:
            self.name = name

        if colour is not None:
            self.colour = colour

        if hoist is not None:
            self.hoist = hoist

        if rank is not None:
            self.rank = rank

        if permissions is not None:
            self.permissions = PermissionsOverwrite._from_overwrite(permissions)

    async def delete(self) -> None:
        """Deletes the role"""
        await self.state.http.delete_role(self.server.id, self.id)

    async def edit(self, **kwargs: Any) -> None:
        """Edits the role

        Parameters
        -----------
        name: str
            The name of the role
        colour: str
            The colour of the role
        hoist: bool
            Whether the role should make the member display seperately in the member list
        rank: int
            The position of the role
        """
        if kwargs.get("colour", Missing) is None:
            remove = ["Colour"]
        else:
            remove = None

        await self.state.http.edit_role(self.server.id, self.id, remove, kwargs)
