from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .category import Category
    from .channel import Channel
    from .file import File
    from .role import Permission, Role

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

class _ServerOptional(TypedDict, total=False):
    nonce: str
    description: str
    categories: list[Category]
    system_messages: SystemMessagesConfig
    roles: list[Role]
    icon: File
    banner: File
    nsfw: bool

class Server(_ServerOptional):
    _id: str
    owner: str
    name: str
    channels: list[str]
    default_permissions: Permission

class _OptionalBannedUser(TypedDict, total=False):
    avatar: File

class BannedUser(_OptionalBannedUser):
    _id: str
    username: str

class _OptionalBan(TypedDict, total=False):
    reason: str

class Ban(_OptionalBan):
    _id: str

class ServerBans(TypedDict):
    users: list[BannedUser]
    bans: list[Ban]
