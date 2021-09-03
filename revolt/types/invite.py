from typing import Literal, TypedDict, Union

__all__ = (
    "GroupInvite",
    "ServerInvite",
    "Invite",
)

class GroupInvite(TypedDict):
    type: Literal["Group"]
    _id: str
    creator: str
    channel: str

class ServerInvite(TypedDict):
    type: Literal["Server"]
    _id: str
    server: str
    creator: str
    channel: str

Invite = Union[ServerInvite, GroupInvite]
