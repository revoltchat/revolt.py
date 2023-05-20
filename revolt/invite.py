from __future__ import annotations

from typing import TYPE_CHECKING


from .asset import Asset
from .utils import Ulid

if TYPE_CHECKING:
    from .state import State
    from .channel import Channel
    from .server import Server
    from .types import Invite as InvitePayload
    from .user import User


__all__ = ("Invite",)

class Invite(Ulid):
    """Represents a server invite.

    Attributes
    -----------
    code: :class:`str`
        The code for the invite
    id: :class:`str`
        Alias for :attr:`code`
    server: :class:`Server`
        The server this invite is for
    channel: :class:`Channel`
        The channel this invite is for
    user_name: :class:`str`
        The name of the user who made the invite
    user: Optional[:class:`User`]
        The user who made the invite, this is only set if this was fetched via :meth:`Server.fetch_invites`
    user_avatar: Optional[:class:`Asset`]
        The invite creator's avatar, if any
    member_count: :class:`int`
        The member count of the server this invite is for
    """

    __slots__ = ("state", "code", "id", "server", "channel", "user_name", "user_avatar", "user", "member_count")

    def __init__(self, data: InvitePayload, code: str, state: State):
        self.state: State = state

        self.code: str = code
        self.id: str = code
        self.server: Server = state.get_server(data["server_id"])
        self.channel: Channel = self.server.get_channel(data["channel_id"])

        self.user_name: str = data["user_name"]
        self.user: User | None = None

        self.user_avatar: Asset | None

        if avatar := data.get("user_avatar"):
            self.user_avatar = Asset(avatar, state)
        else:
            self.user_avatar = None

        self.member_count: int = data["member_count"]

    @staticmethod
    def _from_partial(code: str, server: str, creator: str, channel: str, state: State) -> Invite:
        invite = Invite.__new__(Invite)

        invite.state = state
        invite.code = code
        invite.server = state.get_server(server)
        invite.channel = state.get_channel(channel)
        invite.user = state.get_user(creator)
        invite.user_name = invite.user.name
        invite.user_avatar = invite.user.avatar
        invite.member_count = len(invite.server.members)

        return invite

    async def delete(self) -> None:
        """Deletes the invite"""
        await self.state.http.delete_invite(self.code)
