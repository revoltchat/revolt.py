from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from .channel import Channel
from .permissions import Permissions
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
    __slots__ = ("state", "id", "name", "owner", "default_permissions", "_members", "_roles", "_channels")
    
    def __init__(self, data: ServerPayload, state: State):
        self.state = state
        self.id = data["_id"]
        self.name = data["name"]
        self.owner = state.get_member(self.id, data["owner"])
        self.default_permissions = Permissions(data["default_permissions"])
        
        self._members: dict[str, Member] = {}
        self._roles: dict[str, Role] = {role_id: Role(role, role_id, state) for role_id, role in data.get("roles", {}).items()}
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

    def get_role(self, role_id: str) -> Optional[Role]:
        """Gets a role from the cache
        
        Parameters
        -----------
        id: :class:`str`
            The id of the role
        
        Returns
        --------
        Optional[:class:`Role`]
            The role if found
        """
        return self._roles.get(role_id)

    def get_member(self, member_id: str) -> Optional[Member]:
        """Gets a member from the cache
        
        Parameters
        -----------
        id: :class:`str`
            The id of the member
        
        Returns
        --------
        Optional[:class:`Member`]
            The member if found
        """
        return self._members.get(member_id)

    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Gets a channel from the cache
        
        Parameters
        -----------
        id: :class:`str`
            The id of the channel
        
        Returns
        --------
        Optional[:class:`Channel`]
            The channel if found
        """
        self._channels.get(channel_id)
