from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .member import Member
    from .message import Message
    from .user import User
    from .role import Role


__all__ = (
    "VosoFeature",
    "ApiInfo",
    "Autumn",
    "GetServerMembers",
    "MessageWithUserData",
    "CreateRole",
)


class ApiFeature(TypedDict):
    enabled: bool
    url: str

class VosoFeature(ApiFeature):
    ws: str

class Features(TypedDict):
    email: bool
    invite_only: bool
    captcha: ApiFeature
    autumn: ApiFeature
    january: ApiFeature
    voso: VosoFeature

class ApiInfo(TypedDict):
    revolt: str
    features: Features
    ws: str
    app: str
    vapid: str

class Autumn(TypedDict):
    id: str

class GetServerMembers(TypedDict):
    members: list[Member]
    users: list[User]

class MessageWithUserData(TypedDict):
    messages: list[Message]
    members: NotRequired[list[Member]]
    users: list[User]

class CreateRole(TypedDict):
    id: str
    role: Role