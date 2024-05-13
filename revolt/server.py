from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from .asset import Asset
from .category import Category
from .invite import Invite
from .permissions import Permissions
from .role import Role
from .utils import Ulid
from .channel import Channel, TextChannel, VoiceChannel
from .member import Member

if TYPE_CHECKING:
    from .emoji import Emoji
    from .file import File
    from .state import State
    from .types import Ban
    from .types import Category as CategoryPayload
    from .types import File as FilePayload
    from .types import Server as ServerPayload
    from .types import SystemMessagesConfig
    from .types import Member as MemberPayload

__all__ = ("Server", "SystemMessages", "ServerBan")

class SystemMessages:
    """Holds all the configuration for the server's system message channels"""

    def __init__(self, data: SystemMessagesConfig, state: State):
        self.state: State = state
        self.user_joined_id: str | None = data.get("user_joined")
        self.user_left_id: str | None = data.get("user_left")
        self.user_kicked_id: str | None = data.get("user_kicked")
        self.user_banned_id: str | None = data.get("user_banned")

    @property
    def user_joined(self) -> Optional[TextChannel]:
        """The channel which user join messages get sent in

        Returns
        --------
        Optional[:class:`TextChannel`]
            The channel
        """
        if not self.user_joined_id:
            return

        channel = self.state.get_channel(self.user_joined_id)
        assert isinstance(channel, TextChannel)
        return channel

    @property
    def user_left(self) -> Optional[TextChannel]:
        """The channel which user leave messages get sent in

        Returns
        --------
        Optional[:class:`TextChannel`]
            The channel
        """
        if not self.user_left_id:
            return

        channel = self.state.get_channel(self.user_left_id)
        assert isinstance(channel, TextChannel)
        return channel

    @property
    def user_kicked(self) -> Optional[TextChannel]:
        """The channel which user kick messages get sent in

        Returns
        --------
        Optional[:class:`TextChannel`]
            The channel
        """
        if not self.user_kicked_id:
            return

        channel = self.state.get_channel(self.user_kicked_id)
        assert isinstance(channel, TextChannel)
        return channel

    @property
    def user_banned(self) -> Optional[TextChannel]:
        """The channel which user ban messages get sent in

        Returns
        --------
        Optional[:class:`TextChannel`]
            The channel
        """
        if not self.user_banned_id:
            return

        channel = self.state.get_channel(self.user_banned_id)
        assert isinstance(channel, TextChannel)
        return channel

class Server(Ulid):
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
    default_permissions: :class:`Permissions`
        The permissions for the default role
    """
    __slots__ = ("state", "id", "name", "owner_id", "default_permissions", "_members", "_roles", "_channels", "description", "icon", "banner", "nsfw", "system_messages", "_categories", "_emojis")

    def __init__(self, data: ServerPayload, state: State):
        self.state: State = state
        self.id: str = data["_id"]
        self.name: str = data["name"]
        self.owner_id: str = data["owner"]
        self.description: str | None = data.get("description") or None
        self.nsfw: bool = data.get("nsfw", False)
        self.system_messages: SystemMessages = SystemMessages(data.get("system_messages", cast("SystemMessagesConfig", {})), state)
        self._categories: dict[str, Category] = {data["id"]: Category(data, state) for data in data.get("categories", [])}
        self.default_permissions: Permissions = Permissions(data["default_permissions"])

        self.icon: Asset | None

        if icon := data.get("icon"):
            self.icon = Asset(icon, state)
        else:
            self.icon = None

        self.banner: Asset | None

        if banner := data.get("banner"):
            self.banner = Asset(banner, state)
        else:
            self.banner  = None

        self._members: dict[str, Member] = {}
        self._roles: dict[str, Role] = {role_id: Role(role, role_id, self, state) for role_id, role in data.get("roles", {}).items()}

        self._channels: dict[str, Channel] = {}

        # The api doesnt send us all the channels but sends us all the ids, this is because channels we dont have permissions to see are not sent
        # this causes get_channel to error so we have to first check ourself if its in the cache.

        for channel_id in data["channels"]:
            if channel := state.channels.get(channel_id):
                self._channels[channel_id] = channel

        self._emojis: dict[str, Emoji] = {}

    def _update(self, *, owner: Optional[str] = None, name: Optional[str] = None, description: Optional[str] = None, icon: Optional[FilePayload] = None, banner: Optional[FilePayload] = None, default_permissions: Optional[int] = None, nsfw: Optional[bool] = None, system_messages: Optional[SystemMessagesConfig] = None, categories: Optional[list[CategoryPayload]] = None, channels: Optional[list[str]] = None):
        if owner is not None:
            self.owner_id = owner
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description or None
        if icon is not None:
            self.icon = Asset(icon, self.state)
        if banner is not None:
            self.banner = Asset(banner, self.state)
        if default_permissions is not None:
            self.default_permissions = Permissions(default_permissions)
        if nsfw is not None:
            self.nsfw = nsfw
        if system_messages is not None:
            self.system_messages = SystemMessages(system_messages, self.state)
        if categories is not None:
            self._categories = {data["id"]: Category(data, self.state) for data in categories}
        if channels is not None:
            self._channels = {channel_id: self.state.get_channel(channel_id) for channel_id in channels}

    def _add_member(self, payload: MemberPayload) -> Member:
        member = Member(payload, self, self.state)
        self._members[member.id] = member

        return member

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

    @property
    def emojis(self) -> list[Emoji]:
        """list[:class:`Emoji`] Gets all emojis in the server"""
        return list(self._emojis.values())

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
        try:
            return self._members[member_id]
        except KeyError:
            raise LookupError from None

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
        try:
            return self._channels[channel_id]
        except KeyError:
            raise LookupError from None

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
        try:
            return self._categories[category_id]
        except KeyError:
            raise LookupError from None

    def get_emoji(self, emoji_id: str) -> Emoji:
        """Gets a emoji from the cache

        Parameters
        -----------
        id: :class:`str`
            The id of the emoji

        Returns
        --------
        :class:`Emoji`
            The emoji
        """
        try:
            return self._emojis[emoji_id]
        except KeyError as e:
            raise LookupError from e

    @property
    def owner(self) -> Member:
        """:class:`Member` The owner of the server"""
        return self.get_member(self.owner_id)

    async def set_default_permissions(self, permissions: Permissions) -> None:
        """Sets the default server permissions.
        Parameters
        -----------
        server_permissions: Optional[:class:`ServerPermissions`]
            The new default server permissions
        channel_permissions: Optional[:class:`ChannelPermissions`]
            the new default channel permissions
        """

        await self.state.http.set_server_default_permissions(self.id, permissions.value)

    async def leave_server(self) -> None:
        """Leaves or deletes the server"""
        await self.state.http.delete_leave_server(self.id)

    async def delete_server(self) -> None:
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

        channel = self.state.add_channel(payload)
        self._channels[channel.id] = channel

        return cast(VoiceChannel, channel)

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
        """Fetches all bans in the server

        Returns
        --------
        list[:class:`ServerBan`]
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

        return Role(payload["role"], payload["id"], self, self.state)

    async def create_emoji(self, name: str, file: File, *, nsfw: bool = False) -> Emoji:
        """Creates an emoji

        Parameters
        -----------
        name: :class:`str`
            The name for the emoji
        file: :class:`File`
            The image for the emoji
        nsfw: :class:`bool`
            Whether or not the emoji is nsfw
        """
        payload = await self.state.http.create_emoji(name, file, nsfw, {"type": "Server", "id": self.id})

        return self.state.add_emoji(payload)


class ServerBan:
    """Represents a server ban

    Attributes
    -----------
    reason: Optional[:class:`str`]
        The reason the user was banned
    server: :class:`Server`
        The server the user was banned in
    user_id: :class:`str`
        The id of the user who was banned
    """

    __slots__ = ("reason", "server", "user_id", "state")

    def __init__(self, ban: Ban, state: State):
        self.reason: str | None = ban.get("reason")
        self.server: Server = state.get_server(ban["_id"]["server"])
        self.user_id: str = ban["_id"]["user"]
        self.state: State = state

    async def unban(self) -> None:
        """Unbans the user"""
        await self.state.http.unban_member(self.server.id, self.user_id)
