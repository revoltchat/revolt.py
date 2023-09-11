from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, Optional


from .utils import _Missing, Missing, parse_timestamp

from .asset import Asset
from .permissions import Permissions
from .permissions_calculator import calculate_permissions
from .user import User
from .file import File

if TYPE_CHECKING:
    from .channel import Channel
    from .server import Server
    from .state import State
    from .types import File as FilePayload
    from .types import Member as MemberPayload
    from .role import Role

__all__ = ("Member",)

def flattern_user(member: Member, user: User) -> None:
    for attr in user.__flattern_attributes__:
        setattr(member, attr, getattr(user, attr))

class Member(User):
    """Represents a member of a server, subclasses :class:`User`

    Attributes
    -----------
    nickname: Optional[:class:`str`]
        The nickname of the member if any
    roles: list[:class:`Role`]
        The roles of the member, ordered by the role's rank in decending order
    server: :class:`Server`
        The server the member belongs to
    guild_avatar: Optional[:class:`Asset`]
        The member's guild avatar if any
    """
    __slots__ = ("state", "nickname", "roles", "server", "guild_avatar", "joined_at", "current_timeout")

    def __init__(self, data: MemberPayload, server: Server, state: State):
        user = state.get_user(data["_id"]["user"])

        # due to not having a user payload and only a user object we have to manually add all the attributes instead of calling User.__init__
        flattern_user(self, user)
        user._members[server.id] = self

        self.state: State = state

        self.guild_avatar: Asset | None

        if avatar := data.get("avatar"):
            self.guild_avatar = Asset(avatar, state)
        else:
            self.guild_avatar = None

        roles = [server.get_role(role_id) for role_id in data.get("roles", [])]
        self.roles: list[Role] = sorted(roles, key=lambda role: role.rank, reverse=True)

        self.server: Server = server
        self.nickname: str | None = data.get("nickname")
        self.joined_at: datetime.datetime = parse_timestamp(data["joined_at"])

        self.current_timeout: datetime.datetime | None

        if current_timeout := data.get("timeout"):
            self.current_timeout = parse_timestamp(current_timeout)
        else:
            self.current_timeout = None

    @property
    def avatar(self) -> Optional[Asset]:
        """Optional[:class:`Asset`] The avatar the member is displaying, this includes guild avatars and masqueraded avatar"""
        return self.masquerade_avatar or self.guild_avatar or self.original_avatar

    @property
    def name(self) -> str:
        """:class:`str` The name the user is displaying, this includes (in order) their masqueraded name, display name and orginal name"""
        return self.nickname or self.display_name or self.masquerade_name or self.original_name

    @property
    def mention(self) -> str:
        """:class:`str`: Returns a string that allows you to mention the given member."""
        return f"<@{self.id}>"

    def _update(
        self,
        *,
        nickname: Optional[str] = None,
        avatar: Optional[FilePayload] = None,
        roles: Optional[list[str]] = None,
        timeout: Optional[str | int] = None
    ) -> None:
        if nickname is not None:
            self.nickname = nickname

        if avatar is not None:
            self.guild_avatar = Asset(avatar, self.state)

        if roles is not None:
            member_roles = [self.server.get_role(role_id) for role_id in roles]
            self.roles = sorted(member_roles, key=lambda role: role.rank, reverse=True)

        if timeout is not None:
            self.current_timeout = parse_timestamp(timeout)

    async def kick(self) -> None:
        """Kicks the member from the server"""
        await self.state.http.kick_member(self.server.id, self.id)

    async def ban(self, *, reason: Optional[str] = None) -> None:
        """Bans the member from the server

        Parameters
        -----------
        reason: Optional[:class:`str`]
            The reason for the ban
        """
        await self.state.http.ban_member(self.server.id, self.id, reason)

    async def unban(self) -> None:
        """Unbans the member from the server"""
        await self.state.http.unban_member(self.server.id, self.id)

    async def edit(
        self,
        *,
        nickname: str | None | _Missing = Missing,
        roles: list[Role] | None | _Missing = Missing,
        avatar: File | None | _Missing = Missing,
        timeout: datetime.timedelta | None | _Missing = Missing
    ) -> None:
        """Edits the member

        Parameters
        -----------
        nickname: Union[:class:`str`, :class:`None`]
            The new nickname, or :class:`None` to reset it
        roles: Union[list[:class:`Role`], :class:`None`]
            The new roles for the member, or :class:`None` to clear it
        avatar: Union[:class:`File`, :class:`None`]
            The new server avatar, or :class:`None` to reset it
        timeout: Union[:class:`datetime.timedelta`, :class:`None`]
            The new timeout length for the member, or :class:`None` to reset it
        """
        remove: list[str] = []
        data: dict[str, Any] = {}

        if nickname is None:
            remove.append("Nickname")
        elif nickname is not Missing:
            data["nickname"] = nickname

        if roles is None:
            remove.append("Roles")
        elif not isinstance(roles, _Missing):
            data["roles"] = [role.id for role in roles]

        if avatar is None:
            remove.append("Avatar")
        elif not isinstance(avatar, _Missing):
            data["avatar"] = (await self.state.http.upload_file(avatar, "avatars"))["id"]

        if timeout is None:
            remove.append("Timeout")
        elif not isinstance(timeout, _Missing):
            data["timeout"] = (datetime.datetime.now(datetime.timezone.utc) + timeout).isoformat()

        await self.state.http.edit_member(self.server.id, self.id, remove, data)

    async def timeout(self, length: datetime.timedelta) -> None:
        """Timeouts the member

        Parameters
        -----------
        length: :class:`datetime.timedelta`
            The length of the timeout
        """
        ends_at = datetime.datetime.now(tz=datetime.timezone.utc) + length

        await self.state.http.edit_member(self.server.id, self.id, None, {"timeout": ends_at.isoformat()})

    def get_permissions(self) -> Permissions:
        """Gets the permissions for the member in the server

        Returns
        --------
        :class:`Permissions`
            The members permissions
        """
        return calculate_permissions(self, self.server)

    def get_channel_permissions(self, channel: Channel) -> Permissions:
        """Gets the permissions for the member in the server taking into account the channel as well

        Parameters
        -----------
        channel: :class:`Channel`
            The channel to calculate permissions with

        Returns
        --------
        :class:`Permissions`
            The members permissions
        """
        return calculate_permissions(self, channel)

    def has_permissions(self, **permissions: bool) -> bool:
        """Computes if the member has the specified permissions

        Parameters
        -----------
        permissions: :class:`bool`
            The permissions to check, this also accepted `False` if you need to check if the member does not have the permission

        Returns
        --------
        :class:`bool`
            Whether or not they have the permissions
        """
        calculated_perms = self.get_permissions()

        return all([getattr(calculated_perms, key, False) == value for key, value in permissions.items()])

    def has_channel_permissions(self, channel: Channel, **permissions: bool) -> bool:
        """Computes if the member has the specified permissions, taking into account the channel as well

        Parameters
        -----------
        channel: :class:`Channel`
            The channel to calculate permissions with
        permissions: :class:`bool`
            The permissions to check, this also accepted `False` if you need to check if the member does not have the permission

        Returns
        --------
        :class:`bool`
            Whether or not they have the permissions
        """
        calculated_perms = self.get_channel_permissions(channel)

        return all([getattr(calculated_perms, key, False) == value for key, value in permissions.items()])
