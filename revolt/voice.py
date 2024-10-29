from __future__ import annotations

from typing import TYPE_CHECKING
import livekit
import livekit.rtc


if TYPE_CHECKING:
    from .types import VoiceInformation as VoiceInformationPayload
    from .state import State


__all__ = (
    "VoiceInformation",
    "VoiceState"
)


class VoiceInformation:
    """Holds information on the voice configuration of the text channel

    Attributes
    -----------
    max_users: Optional[:class:`int`]
        How many users can be in the voice at once
    """
    def __init__(self, data: VoiceInformationPayload) -> None:
        self.max_users: int | None =  data.get("max_users", None)

class VoiceState:
    def __init__(self, state: State, token: str) -> None:
        self.state = state
        self.token = token
        self.room = livekit.rtc.Room()

    async def connect(self):
        await self.room.connect(self.state.api_info["features"]["livekit"]["url"], self.token)