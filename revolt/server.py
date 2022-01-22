from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from .asset import Asset
from .category import Category
from .channel import Channel, VoiceChannel
from .invite import Invite
from .permissions import ChannelPermissions, ServerPermissions
from .role import Role

if TYPE_CHECKING:
    from .channel import TextChannel
    from .member import Member
    from .state import State
    from .types import Category as CategoryPayload
    from .types import File as FilePayload
    from .types import Permission as PermissionPayload
    from .types import Server as ServerPayload
    from .types import SystemMessagesConfig, Ban


__all__ = ("Server", "SystemMessages")

class SystemMessages:
    def __init__(self, data: SystemMessagesConfig, state: State):
        self.state = state
        self.user_joined_id = data.get("user_joined")
        self.user_left_id = data.get("user_left")
        self.user_kicked_id = data.get("user_kicked")
        self.user_banned_id = data.get("user_banned")

    @property
    def user_joined(self) -> Optional[TextChannel]:
        if not self.user_joined_id:
            return

        channel = self.state.get_channel(self.user_joined_id)
        assert isinstance(channel, TextChannel)
        return channel

    @property
    def user_left(self) -> Optional[TextChannel]:
        if not self.user_left_id:
            return

        channel = self.state.get_channel(self.user_left_id)
        assert isinstance(channel, TextChannel)
        return channel

    @property
    def user_kicked(self) -> Optional[TextChannel]:
        if not self.user_kicked_id:
            return

        channel = self.state.get_channel(self.user_kicked_id)
        assert isinstance(channel, TextChannel)
        return channel

    @property
    def user_banned(self) -> Optional[TextChannel]:
        if not self.user_banned_id:
            return

        channel = self.state.get_channel(self.user_banned_id)
        assert isinstance(channel, TextChannel)
        return channel

class Server:
    """Represents a server

    Attributes
    -----------
    id: :class:`str`
        The id of the server
    name: :class:`str`
        The name of the server
    owner_id: :class:`str`
        The owner's id of the server
    description: Optional[:class:`str`]
        The servers description
    nsfw: :class:`bool`
        Whether the server is nsfw or not
    system_messages: :class:`SystemMessages`
        The system message config for the server
    icon: Optional[:class:`Asset`]
        The servers icon
    banner: Optional[:class:`Asset`]
        The servers banner
    """
    __slots__ = ("state", "id", "name", "owner_id", "default_server_permissions", "default_channel_permissions", "_members", "_roles", "_channels", "description", "icon", "banner", "nsfw", "system_messages", "_categories")

    def __init__(self, data: ServerPayload, state: State):
        self.state = state
        self.id = data["_id"]
        self.name = data["name"]
        self.owner_id = data["owner"]
        self.default_server_permissions = ServerPermissions._from_value(data["default_permissions"][0])
        self.default_channel_permissions = ChannelPermissions._from_value(data["default_permissions"][1])
        self.description = data.get("description") or None
        self.nsfw = data.get("nsfw", False)
        self.system_messages = SystemMessages(data.get("system_messages", cast(SystemMessagesConfig, {})), state)
        self._categories = {data["id"]: Category(data, state) for data in data.get("categories", [])}

        if icon := data.get("icon"):
            self.icon = Asset(icon, state)
        else:
            self.icon = None

        if banner := data.get("banner"):
            self.banner = Asset(banner, state)
        else:
            self.banner  = None

        self._members: dict[str, Member] = {}
        self._roles: dict[str, Role] = {role_id: Role(role, role_id, self, state) for role_id, role in data.get("roles", {}).items()}

        self._channels: dict[str, Channel] = {channel_id: state.get_channel(channel_id) for channel_id in data.get("channels", [])}

    def _update(self, *, owner: Optional[str] = None, name: Optional[str] = None, description: Optional[str] = None, icon: Optional[FilePayload] = None, banner: Optional[FilePayload] = None, default_permissions: Optional[PermissionPayload] = None, nsfw: Optional[bool] = None, system_messages: Optional[SystemMessagesConfig] = None, categories: Optional[list[CategoryPayload]] = None):
        if owner:
            self.owner_id = owner
        if name:
            self.name = name
        if description is not None:
            self.description = description or None
        if icon:
            self.icon = Asset(icon, self.state)
        if banner:
            self.banner = Asset(banner, self.state)
        if default_permissions:
            self.default_server_permissions = ServerPermissions._from_value(default_permissions[0])
            self.default_channel_permissions = ChannelPermissions._from_value(default_permissions[1])
        if nsfw is not None:
            self.nsfw = nsfw
        if system_messages is not None:
            self.system_messages = SystemMessages(system_messages, self.state)
        if categories is not None:
            self._categories = {data["id"]: Category(data, self.state) for data in categories}

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

    @property
    def categories(self) -> list[Category]:
        """list[:class:`Category`] Gets all categories in the server"""
        return list(self._categories.values())

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

    def get_category(self, category_id: str) -> Category:
        """Gets a category from the cache

        Parameters
        -----------
        id: :class:`str`
            The id of the category

        Returns
        --------
        :class:`Category`
            The category
        """
        return self._categories[category_id]

    @property
    def owner(self) -> Member:
        """:class:`Member` The owner of the server"""
        return self.get_member(self.owner_id)

    async def set_default_permissions(self, *, server_permissions: Optional[ServerPermissions] = None, channel_permissions: Optional[ChannelPermissions] = None) -> None:
        """Sets the default server permissions.
        Parameters
        -----------
        server_permissions: Optional[:class:`ServerPermissions`]
            The new default server permissions
        channel_permissions: Optional[:class:`ChannelPermissions`]
            the new default channel permissions
        """
        server_value = (server_permissions or self.default_server_permissions).value
        channel_value = (channel_permissions or self.default_channel_permissions).value

        await self.state.http.set_default_permissions(self.id, server_value, channel_value)

    async def leave_server(self):
        """Leaves or deletes the server"""
        await self.state.http.delete_leave_server(self.id)

    async def delete_server(self):
        """Leaves or deletes a server, alias to :meth`Server.leave_server`"""
        await self.leave_server()

    async def create_text_channel(self, *, name: str, description: Optional[str] = None) -> TextChannel:
        """Creates a text channel in the server

        Parameters
        -----------
        name: :class:`str`
            The name of the channel
        description: Optional[:class:`str`]
            The channel's description

        Returns
        --------
        :class:`TextChannel`
            The text channel that was just created
        """
        payload = await self.state.http.create_channel(self.id, "Text", name, description)

        channel = TextChannel(payload, self.state)
        self._channels[channel.id] = channel

        return channel

    async def create_voice_channel(self, *, name: str, description: Optional[str] = None) -> VoiceChannel:
        """Creates a voice channel in the server

        Parameters
        -----------
        name: :class:`str`
            The name of the channel
        description: Optional[:class:`str`]
            The channel's description

        Returns
        --------
        :class:`VoiceChannel`
            The voice channel that was just created
        """
        payload = await self.state.http.create_channel(self.id, "Voice", name, description)

        channel = VoiceChannel(payload, self.state)
        self._channels[channel.id] = channel

        return channel

    async def fetch_invites(self) -> list[Invite]:
        """Fetches all invites in the server

        Returns
        --------
        list[:class:`Invite`]
        """
        invite_payloads = await self.state.http.fetch_server_invites(self.id)

        return [Invite._from_partial(payload["_id"], payload["server"], payload["creator"], payload["channel"], self.state) for payload in invite_payloads]

    async def fetch_member(self, member_id: str) -> Member:
        """Fetches a member from this server

        Parameters
        -----------
        member_id: :class:`str`
            The id of the member you are fetching

        Returns
        --------
        :class:`Member`
            The member with the matching id
        """
        payload = await self.state.http.fetch_member(self.id, member_id)

        return Member(payload, self, self.state)

    async def fetch_bans(self) -> list[ServerBan]:
        """Fetches all invites in the server

        Returns
        --------
        list[:class:`Invite`]
        """
        payload = await self.state.http.fetch_bans(self.id)

        return [ServerBan(ban, self.state) for ban in payload["bans"]]

    async def create_role(self, name: str) -> Role:
        """Creates a role in the server

        Parameters
        -----------
        name: :class:`str`
            The name of the role


        Returns
        --------
        :class:`Role`
            The role that was just created
        """
        payload = await self.state.http.create_role(self.id, name)

        return Role(payload, name, self, self.state)

class ServerBan:
    def __init__(self, ban: Ban, state: State):
        self.reason = ban.get("reason")
        self.server = state.get_server(ban["_id"]["server"])
        self.user = state.get_user(ban["_id"]["user"])
        self.state = state

    async def unban(self):
        """Unbans the user"""
        await self.state.http.unban_member(self.server.id, self.user.id)
