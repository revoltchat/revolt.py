from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, Union

from revolt.utils import Missing

from .asset import Asset
from .enums import ChannelType
from .messageable import Messageable
from .permissions import ChannelPermissions
from .utils import Missing

if TYPE_CHECKING:
    from .message import Message
    from .role import Role
    from .server import Server
    from .state import State
    from .types import Channel as ChannelPayload
    from .types import DMChannel as DMChannelPayload
    from .types import GroupDMChannel as GroupDMChannelPayload
    from .types import SavedMessages as SavedMessagesPayload
    from .types import TextChannel as TextChannelPayload
    from .types import VoiceChannel as VoiceChannelPayload
    from .user import User

__all__ = ("DMChannel", "GroupDMChannel", "SavedMessageChannel", "TextChannel", "VoiceChannel", "Channel")

class EditableChannel:
    __slots__ = ()

    state: State
    id: str

    async def edit(self, **kwargs):
        if kwargs.get("icon", Missing) == None:
            remove = "Icon"
        elif kwargs.get("description", Missing) == None:
            remove = "Description"
        else:
            remove = None

        await self.state.http.edit_channel(self.id, remove, kwargs)

class Channel:
    """Base class for all channels
    
    Attributes
    -----------
    id: :class:`str`
        The id of the channel
    channel_type: ChannelType
        The type of the channel
    """
    __slots__ = ("state", "id", "channel_type", "server_id")

    def __init__(self, data: ChannelPayload, state: State):
        self.state = state
        self.id = data["_id"]
        self.channel_type = ChannelType(data["channel_type"])
        self.server_id = ""

    async def _get_channel_id(self) -> str:
        return self.id

    def _update(self):
        pass

    async def delete(self):
        """Deletes or closes the channel"""
        await self.state.http.close_channel(self.id)

    @property
    def server(self) -> Server:
        """:class:`Server` The server this voice channel belongs too"""
        return self.state.get_server(self.server_id)

class SavedMessageChannel(Channel, Messageable):
    """The Saved Message Channel"""
    def __init__(self, data: SavedMessagesPayload, state: State):
        super().__init__(data, state)

class DMChannel(Channel, Messageable):
    """A DM channel"""
    def __init__(self, data: DMChannelPayload, state: State):
        super().__init__(data, state)

class GroupDMChannel(Channel, Messageable, EditableChannel):
    """A group DM channel

    Attributes
    -----------
    recipients: list[:class:`User`]
        The recipients of the group dm channel
    name: :class:`str`
        The name of the group dm channel
    owner: :class:`User`
        The user who created the group dm channel
    icon: Optional[:class:`Asset`]
        The icon of the group dm channel
    permissions: :class:`ChannelPermissions`
        The permissions of the users inside the group dm channel
    """

    __slots__ = ("recipients", "name", "owner", "permissions", "icon")

    def __init__(self, data: GroupDMChannelPayload, state: State):
        super().__init__(data, state)
        self.recipients = [state.get_user(user_id) for user_id in data["recipients"]]
        self.name = data["name"]
        self.owner = state.get_user(data["owner"])

        if icon := data.get("icon"):
            self.icon = Asset(icon, state)
        else:
            self.icon = None

        if perms := data.get("permissions"):
            self.permissions = ChannelPermissions._from_value(perms)
        else:
            self.permissions = ChannelPermissions._from_value(0)

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

class TextChannel(Channel, Messageable, EditableChannel):
    __slots__ = ("name", "description", "last_message_id", "server_id", "default_permissions", "role_permissions", "icon")

    """A text channel

    Attributes
    -----------
    name: :class:`str`
        The name of the text channel
    server_id: :class:`str`
        The id of the server this text channel belongs to
    last_message_id: Optional[:class:`str`]
        The id of the last message in this channel, if any
    default_permissions: :class:`ChannelPermissions`
        The default permissions for all users in the text channel
    role_permissions: dict[:class:`str`, :class:`ChannelPermissions`]
        A dictionary of role id's to the permissions of that role in the text channel
    icon: Optional[:class:`Asset`]
        The icon of the text channel, if any
    """
    def __init__(self, data: TextChannelPayload, state: State):
        super().__init__(data, state)

        self.server_id = data["server"]
        self.name = data["name"]
        self.description = data.get("description")

        last_message_id = data.get("last_message")
        self.last_message_id = last_message_id

        self.default_permissions = ChannelPermissions._from_value(data.get("default_permissions", 0))
        self.role_permissions = {role_id: ChannelPermissions._from_value(perms) for role_id, perms in data.get("role_permissions", {}).items()}

        if icon := data.get("icon"):
            self.icon = Asset(icon, state)
        else:
            self.icon = None

    def _get_channel_id(self) -> str:
        return self.id

    @property
    def last_message(self) -> Optional[Message]:
        """Gets the last message from the channel, shorthand for `client.get_message(channel.last_message_id)`

        Returns
        --------
        :class:`Message` the last message in the channel
        """

        if not self.last_message_id:
            return

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

class VoiceChannel(Channel, EditableChannel):
    """A voice channel

    Attributes
    -----------
    name: :class:`str`
        The name of the voice channel
    server_id: :class:`str`
        The id of the server this voice channel belongs to
    last_message_id: Optional[:class:`str`]
        The id of the last message in this channel, if any
    default_permissions: :class:`ChannelPermissions`
        The default permissions for all users in the voice channel
    role_permissions: dict[:class:`str`, :class:`ChannelPermissions`]
        A dictionary of role id's to the permissions of that role in the voice channel
    icon: Optional[:class:`Asset`]
        The icon of the voice channel, if any
    """
    def __init__(self, data: VoiceChannelPayload, state: State):
        super().__init__(data, state)

        self.server_id = data["server"]
        self.name = data["name"]
        self.description = data.get("description")

        if perms := data.get("default_permissions"):
            self.default_permissions = ChannelPermissions._from_value(perms)
        else:
            self.default_permissions = ChannelPermissions._from_value(0)

        if role_perms := data.get("role_permissions"):
            self.role_permissions = {role_id: ChannelPermissions._from_value(perms) for role_id, perms in role_perms.items()}
        else:
            self.role_permissions = {}

        if icon := data.get("icon"):
            self.icon = Asset(icon, state)
        else:
            self.icon = None

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

def channel_factory(data: ChannelPayload, state: State) -> Union[DMChannel, GroupDMChannel, SavedMessageChannel, TextChannel, VoiceChannel]:
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
