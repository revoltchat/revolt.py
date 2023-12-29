from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Union

from .asset import Asset
from .enums import ChannelType
from .messageable import Messageable
from .permissions import Permissions, PermissionsOverwrite
from .utils import Missing, Ulid

if TYPE_CHECKING:
    from .message import Message
    from .role import Role
    from .server import Server
    from .state import State
    from .types import Channel as ChannelPayload
    from .types import DMChannel as DMChannelPayload
    from .types import File as FilePayload
    from .types import GroupDMChannel as GroupDMChannelPayload
    from .types import Overwrite as OverwritePayload
    from .types import SavedMessages as SavedMessagesPayload
    from .types import ServerChannel as ServerChannelPayload
    from .types import TextChannel as TextChannelPayload
    from .user import User

__all__ = ("DMChannel", "GroupDMChannel", "SavedMessageChannel", "TextChannel", "VoiceChannel", "Channel", "ServerChannel")

class EditableChannel:
    __slots__ = ()

    state: State
    id: str

    async def edit(self, **kwargs: Any) -> None:
        """Edits the channel

        Passing ``None`` to the parameters that accept it will remove them.

        Parameters
        -----------
        name: str
            The new name for the channel
        description: Optional[str]
            The new description for the channel
        owner: User
            The new owner for the group dm channel
        icon: Optional[File]
            The new icon for the channel
        nsfw: bool
            Sets whether the channel is nsfw or not
        """
        remove: list[str] = []

        if kwargs.get("icon", Missing) == None:
            remove.append("Icon")
        elif kwargs.get("description", Missing) == None:
            remove.append("Description")

        if icon := kwargs.get("icon"):
            asset = await self.state.http.upload_file(icon, "icons")
            kwargs["icon"] = asset["id"]

        if owner := kwargs.get("owner"):
            kwargs["owner"] = owner.id

        await self.state.http.edit_channel(self.id, remove, kwargs)

class Channel(Ulid):
    """Base class for all channels

    Attributes
    -----------
    id: :class:`str`
        The id of the channel
    channel_type: ChannelType
        The type of the channel
    server_id: Optional[:class:`str`]
        The server id of the chanel, if any
    """
    __slots__ = ("state", "id", "channel_type", "server_id")

    def __init__(self, data: ChannelPayload, state: State):
        self.state: State = state
        self.id: str = data["_id"]
        self.channel_type: ChannelType = ChannelType(data["channel_type"])
        self.server_id: Optional[str] = None

    async def _get_channel_id(self) -> str:
        return self.id

    def _update(self, **_: Any) -> None:
        pass

    async def delete(self) -> None:
        """Deletes or closes the channel"""
        await self.state.http.close_channel(self.id)

    @property
    def server(self) -> Server:
        """:class:`Server` The server this voice channel belongs too

        Raises
        -------
        :class:`LookupError`
            Raises if the channel is not part of a server
        """
        if not self.server_id:
            raise LookupError

        return self.state.get_server(self.server_id)

    @property
    def mention(self) -> str:
        """:class:`str`: Returns a string that allows you to mention the given channel."""
        return f"<#{self.id}>"


class SavedMessageChannel(Channel, Messageable):
    """The Saved Message Channel"""
    def __init__(self, data: SavedMessagesPayload, state: State):
        super().__init__(data, state)

class DMChannel(Channel, Messageable):
    """A DM channel

    Attributes
    -----------
    last_message_id: Optional[:class:`str`]
        The id of the last message in this channel, if any
    """

    __slots__ = ("last_message_id", "recipient_ids")

    def __init__(self, data: DMChannelPayload, state: State):
        super().__init__(data, state)

        self.recipient_ids: list[str] = data["recipients"]
        self.last_message_id: str | None = data.get("last_message_id")

    @property
    def recipients(self) -> tuple[User, User]:
        a, b = self.recipient_ids

        return (self.state.get_user(a), self.state.get_user(b))

    @property
    def recipient(self) -> User:
        if self.recipient_ids[0] != self.state.user_id:
            user_id = self.recipient_ids[0]
        else:
            user_id = self.recipient_ids[1]

        return self.state.get_user(user_id)

    @property
    def last_message(self) -> Message:
        """Gets the last message from the channel, shorthand for `client.get_message(channel.last_message_id)`

        Returns
        --------
        :class:`Message` the last message in the channel
        """

        if not self.last_message_id:
            raise LookupError

        return self.state.get_message(self.last_message_id)

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
    description: Optional[:class:`str`]
        The description of the channel, if any
    last_message_id: Optional[:class:`str`]
        The id of the last message in this channel, if any
    """

    __slots__ = ("recipient_ids", "name", "owner_id", "permissions", "icon", "description", "last_message_id")

    def __init__(self, data: GroupDMChannelPayload, state: State):
        super().__init__(data, state)
        self.recipient_ids: list[str] = data["recipients"]
        self.name: str = data["name"]
        self.owner_id: str = data["owner"]
        self.description: str | None = data.get("description")
        self.last_message_id: str | None = data.get("last_message_id")

        self.icon: Asset | None

        if icon := data.get("icon"):
            self.icon = Asset(icon, state)
        else:
            self.icon = None

        self.permissions: Permissions = Permissions(data.get("permissions", 0))

    def _update(self, *, name: Optional[str] = None, recipients: Optional[list[str]] = None, description: Optional[str] = None) -> None:
        if name is not None:
            self.name = name

        if recipients is not None:
            self.recipient_ids = recipients

        if description is not None:
            self.description = description

    @property
    def recipients(self) -> list[User]:
        return [self.state.get_user(user_id) for user_id in self.recipient_ids]

    @property
    def owner(self) -> User:
        return self.state.get_user(self.owner_id)

    async def set_default_permissions(self, permissions: Permissions) -> None:
        """Sets the default permissions for a group.
        Parameters
        -----------
        permissions: :class:`ChannelPermissions`
            The new default group permissions
        """
        await self.state.http.set_group_channel_default_permissions(self.id, permissions.value)

    @property
    def last_message(self) -> Message:
        """Gets the last message from the channel, shorthand for `client.get_message(channel.last_message_id)`

        Returns
        --------
        :class:`Message` the last message in the channel
        """

        if not self.last_message_id:
            raise LookupError

        return self.state.get_message(self.last_message_id)

class ServerChannel(Channel):
    """Base class for all guild channels

    Attributes
    -----------
    server_id: :class:`str`
        The id of the server this text channel belongs to
    name: :class:`str`
        The name of the text channel
    description: Optional[:class:`str`]
        The description of the channel, if any
    nsfw: bool
        Sets whether the channel is nsfw or not
    default_permissions: :class:`ChannelPermissions`
        The default permissions for all users in the text channel
    """
    def __init__(self, data: ServerChannelPayload, state: State):
        super().__init__(data, state)

        self.server_id: Optional[str] = data["server"]
        self.name: str = data["name"]
        self.description: Optional[str] = data.get("description")
        self.nsfw: bool = data.get("nsfw", False)
        self.active: bool = False
        self.default_permissions: PermissionsOverwrite = PermissionsOverwrite._from_overwrite(data.get("default_permissions", {"a": 0, "d": 0}))

        permissions: dict[str, PermissionsOverwrite] = {}

        for role_name, overwrite_data in data.get("role_permissions", {}).items():
            overwrite = PermissionsOverwrite._from_overwrite(overwrite_data)
            permissions[role_name] = overwrite

        self.permissions: dict[str, PermissionsOverwrite] = permissions

        self.icon: Asset | None

        if icon := data.get("icon"):
            self.icon = Asset(icon, state)
        else:
            self.icon = None

    async def set_default_permissions(self, permissions: PermissionsOverwrite) -> None:
        """Sets the default permissions for the channel.
        Parameters
        -----------
        permissions: :class:`ChannelPermissions`
            The new default channel permissions
        """
        allow, deny = permissions.to_pair()
        await self.state.http.set_guild_channel_default_permissions(self.id, allow.value, deny.value)

    async def set_role_permissions(self, role: Role, permissions: PermissionsOverwrite) -> None:
        """Sets the permissions for a role in the channel.
        Parameters
        -----------
        permissions: :class:`ChannelPermissions`
            The new channel permissions
        """
        allow, deny = permissions.to_pair()

        await self.state.http.set_guild_channel_role_permissions(self.id, role.id, allow.value, deny.value)

    def _update(self, *, name: Optional[str] = None, description: Optional[str] = None, icon: Optional[FilePayload] = None, nsfw: Optional[bool] = None, active: Optional[bool] = None, role_permissions: Optional[dict[str, OverwritePayload]] = None, default_permissions: Optional[OverwritePayload] = None):
        if name is not None:
            self.name = name

        if description is not None:
            self.description = description

        if icon is not None:
            self.icon = Asset(icon, self.state)

        if nsfw is not None:
            self.nsfw = nsfw

        if active is not None:
            self.active = active

        if role_permissions is not None:
            permissions = {}

            for role_name, overwrite_data in role_permissions.items():
                overwrite = PermissionsOverwrite._from_overwrite(overwrite_data)
                permissions[role_name] = overwrite

            self.permissions = permissions

        if default_permissions is not None:
            self.default_permissions = PermissionsOverwrite._from_overwrite(default_permissions)

class TextChannel(ServerChannel, Messageable, EditableChannel):
    """A text channel

    Subclasses :class:`ServerChannel` and :class:`Messageable`

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
    description: Optional[:class:`str`]
        The description of the channel, if any
    """

    __slots__ = ("name", "description", "last_message_id", "default_permissions", "icon", "overwrites")

    def __init__(self, data: TextChannelPayload, state: State):
        super().__init__(data, state)

        self.last_message_id: str | None = data.get("last_message_id")

    async def _get_channel_id(self) -> str:
        return self.id

    @property
    def last_message(self) -> Message:
        """Gets the last message from the channel, shorthand for `client.get_message(channel.last_message_id)`

        Returns
        --------
        :class:`Message` the last message in the channel
        """

        if not self.last_message_id:
            raise LookupError

        return self.state.get_message(self.last_message_id)

class VoiceChannel(ServerChannel, EditableChannel):
    """A voice channel

    Subclasses :class:`ServerChannel`

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
    description: Optional[:class:`str`]
        The description of the channel, if any
    """

def channel_factory(data: ChannelPayload, state: State) -> Union[DMChannel, GroupDMChannel, SavedMessageChannel, TextChannel, VoiceChannel]:
    if data["channel_type"] == "SavedMessages":
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
