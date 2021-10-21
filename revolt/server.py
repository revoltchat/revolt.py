from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from .channel import Channel
from .permissions import ServerPermissions
from .role import Role

if TYPE_CHECKING:
    from .member import Member
    from .state import State
    from .types import Server as ServerPayload


__all__ = ("Server",)

class Server:
    """Represents a server
    
    Attributes
    -----------
    id: :class:`str`
        The id of the server
    name: :class:`str`
        The name of the server
    owner: Optional[:class:`Member`]
        The owner of the server
    """
    __slots__ = ("state", "id", "name", "owner_id", "default_permissions", "_members", "_roles", "_channels")
    
    def __init__(self, data: ServerPayload, state: State):
        self.state = state
        self.id = data["_id"]
        self.name = data["name"]
        self.owner_id = data["owner"]
        self.default_permissions = ServerPermissions(*data["default_permissions"])
        
        self._members: dict[str, Member] = {}
        self._roles: dict[str, Role] = {role_id: Role(role, role_id, state, self) for role_id, role in data.get("roles", {}).items()}
        channels = cast(list[Channel], list(filter(bool, [state.get_channel(channel_id) for channel_id in data["channels"]])))
        self._channels: dict[str, Channel] = {channel.id: channel for channel in channels}

    @property
    def roles(self) -> list[Role]:
        """list[:class:`Role`] Gets all roles in the server in decending order"""
        return list(self._roles.values())
    
    @property
    def members(self) -> list[Member]:
        """list[:class:`Member`] Gets all members in the server"""
        return list(self._members.values())

    @property
    def channels(self) -> list[Channel]:
        """list[:class:`Member`] Gets all channels in the server"""
        return list(self._channels.values())

    def get_role(self, role_id: str) -> Role:
        """Gets a role from the cache
        
        Parameters
        -----------
        id: :class:`str`
            The id of the role
        
        Returns
        --------
        :class:`Role`
            The role
        """
        return self._roles[role_id]

    def get_member(self, member_id: str) -> Member:
        """Gets a member from the cache
        
        Parameters
        -----------
        id: :class:`str`
            The id of the member
        
        Returns
        --------
        :class:`Member`
            The member
        """
        return self._members[member_id]

    def get_channel(self, channel_id: str) -> Channel:
        """Gets a channel from the cache
        
        Parameters
        -----------
        id: :class:`str`
            The id of the channel
        
        Returns
        --------
        :class:`Channel`
            The channel
        """
        return self._channels[channel_id]

    @property
    def owner(self) -> Optional[Member]:
        owner_id = self.owner_id

        if not owner_id:
            return

        return self.get_member(owner_id)

    async def set_default_permissions(self, permissions: ServerPermissions) -> None:
        """Sets the default server permissions.
        Parameters
        -----------
        permissions: :class:`ServerPermissions`
            The new default server permissions
        """
        await self.state.http.set_default_permissions(self.id, *permissions.value)
