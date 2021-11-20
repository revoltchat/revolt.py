from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from .enums import ChannelType
from .messageable import Messageable
from .permissions import ChannelPermissions

if TYPE_CHECKING:
    from .message import Message
    from .role import Role
    from .server import Server
    from .state import State
    from .types import Channel as ChannelPayload
    from .types import DMChannel as DMChannelPayload
    from .types import Group as GroupDMChannelPayload
    from .types import SavedMessages as SavedMessagesPayload
    from .types import TextChannel as TextChannelPayload
    from .types import VoiceChannel as VoiceChannelPayload
    from .user import User

__all__ = ("Channel",)

class Channel:
    """Base class for all channels
    
    Attributes
    -----------
    id: :class:`str`
        The id of the channel
    channel_type: ChannelType
        The type of the channel
    server: Optional[:class:`Server`]
        The server the channel is part of
    """
    __slots__ = ("state", "id", "channel_type", "server_id")

    def __init__(self, data: ChannelPayload, state: State):
        self.state = state
        self.id = data["_id"]
        self.channel_type = ChannelType(data["channel_type"])
        self.server_id = ""

    @property
    def server(self) -> Optional[Server]:
        return self.state.get_server(self.server_id) if self.server_id else None

    def _update(self):
        pass

class SavedMessageChannel(Channel, Messageable):
    """The Saved Message Channel"""
    def __init__(self, data: SavedMessagesPayload, state: State):
        super().__init__(data, state)

class DMChannel(Channel, Messageable):
    """A DM channel"""
    def __init__(self, data: DMChannelPayload, state: State):
        super().__init__(data, state)

class GroupDMChannel(Channel, Messageable):
    __slots__ = ("recipients", "name", "owner", "permissions")

    """A group DM channel"""
    def __init__(self, data: GroupDMChannelPayload, state: State):
        super().__init__(data, state)
        self.recipients = [state.get_user(user_id) for user_id in data["recipients"]]
        self.name = data["name"]
        self.owner = state.get_user(data["owner"])

        if perms := data.get("permissions"):
            self.permissions = ChannelPermissions._from_value(perms)

    def _update(self, *, name: Optional[str] = None, recipients: Optional[list[str]] = None):
        if name:
            self.name = name

        if recipients:
            self.recipients = [self.state.get_user(user_id) for user_id in recipients]

    async def set_default_permissions(self, permissions: ChannelPermissions) -> None:
        """Sets the default permissions for a group.
        Parameters
        -----------
        permissions: :class:`ChannelPermissions`
            The new default group permissions
        """
        await self.state.http.set_channel_default_permissions(self.id, permissions.value)

class TextChannel(Channel, Messageable):
    __slots__ = ("name", "description", "last_message_id", "server_id", "default_permissions", "role_permissions")

    """A text channel"""
    def __init__(self, data: TextChannelPayload, state: State):
        super().__init__(data, state)

        self.server_id = data["server"]
        self.name = data["name"]
        self.description = data.get("description")

        last_message_id = data.get("last_message")
        self.last_message_id = last_message_id

        if perms := data.get("default_permissions"):
            self.default_permissions = ChannelPermissions._from_value(perms)

        if role_perms := data.get("role_permissions"):
            self.role_permissions = {role_id: ChannelPermissions._from_value(perms) for role_id, perms in role_perms.items()}

    def _get_channel_id(self) -> str:
        return self.id

    @property
    def last_message(self) -> Message:
        return self.state.get_message(self.last_message_id)

    def _update(self, *, name: Optional[str] = None, description: Optional[str] = None):
        if name:
            self.name = name

        if description:
            self.description = description

    async def set_default_permissions(self, permissions: ChannelPermissions) -> None:
        """Sets the default permissions for a channel.
        Parameters
        -----------
        permissions: :class:`ChannelPermissions`
            The new default channel permissions
        """
        await self.state.http.set_channel_default_permissions(self.id, permissions.value)

    async def set_role_permissions(self, role: Role, permissions: ChannelPermissions) -> None:
        """Sets the permissions for a role in a channel.
        Parameters
        -----------
        permissions: :class:`ChannelPermissions`
            The new channel permissions
        """
        await self.state.http.set_channel_role_permissions(self.id, role.id, permissions.value)

class VoiceChannel(Channel):
    """A voice channel"""
    def __init__(self, data: VoiceChannelPayload, state: State):
        super().__init__(data, state)

        self.server_id = data["server"]
        self.name = data["name"]
        self.description = data.get("description")

        if perms := data.get("default_permissions"):
            self.default_permissions = ChannelPermissions._from_value(perms)

        if role_perms := data.get("role_permissions"):
            self.role_permissions = {role_id: ChannelPermissions._from_value(perms) for role_id, perms in role_perms.items()}

    def _update(self, *, name: Optional[str] = None, description: Optional[str] = None):
        if name:
            self.name = name

        if description:
            self.description = description

    async def set_default_permissions(self, permissions: ChannelPermissions) -> None:
        """Sets the default permissions for a voice channel.
        Parameters
        -----------
        permissions: :class:`ChannelPermissions`
            The new default channel permissions
        """
        await self.state.http.set_channel_default_permissions(self.id, permissions.value)

    async def set_role_permissions(self, role: Role, permissions: ChannelPermissions) -> None:
        """Sets the permissions for a role in a voice channel
        Parameters
        -----------
        permissions: :class:`ChannelPermissions`
            The new channel permissions
        """
        await self.state.http.set_channel_role_permissions(self.id, role.id, permissions.value)

def channel_factory(data: ChannelPayload, state: State) -> Channel:
    if data["channel_type"] == "SavedMessage":
        return SavedMessageChannel(data, state)
    elif data["channel_type"] == "DirectMessage":
        return DMChannel(data, state)
    elif data["channel_type"] == "Group":
        return GroupDMChannel(data, state)
    elif data["channel_type"] == "TextChannel":
        return TextChannel(data, state)
    elif data["channel_type"] == "VoiceChannel":
        return VoiceChannel(data, state)
    else:
        raise Exception
