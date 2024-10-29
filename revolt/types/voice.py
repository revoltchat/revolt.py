from __future__ import annotations

from typing import TypedDict

from typing_extensions import NotRequired

__all__ = (
    "VoiceInformation",
    "ChannelVoiceState"
)

class VoiceInformation(TypedDict):
    max_users: NotRequired[int]

class ChannelVoiceState(TypedDict):
    id: str
    participants: list[UserVoiceState]

class UserVoiceState(TypedDict):
    id: str
    can_receive: bool
    can_publish: bool
    screensharing: bool
    camera: bool