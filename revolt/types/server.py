from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .category import Category
    from .file import File
    from .role import Role

__all__ = (
    "Server",
    "BannedUser",
    "Ban",
    "ServerBans",
    "SystemMessagesConfig"
)

class SystemMessagesConfig(TypedDict, total=False):
    user_joined: str
    user_left: str
    user_kicked: str
    user_banned: str


class Server(TypedDict):
    _id: str
    owner: str
    name: str
    channels: list[str]
    default_permissions: int
    nonce: NotRequired[str]
    description: NotRequired[str]
    categories: NotRequired[list[Category]]
    system_messages: NotRequired[SystemMessagesConfig]
    roles: NotRequired[dict[str, Role]]
    icon: NotRequired[File]
    banner: NotRequired[File]
    nsfw: NotRequired[bool]

class BannedUser(TypedDict):
    _id: str
    username: str
    avatar: NotRequired[File]

class BanId(TypedDict):
    server: str
    user: str

class Ban(TypedDict):
    _id: BanId
    reason: NotRequired[str]

class ServerBans(TypedDict):
    users: list[BannedUser]
    bans: list[Ban]
