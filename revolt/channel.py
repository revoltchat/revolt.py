from __future__ import annotations

from typing import TYPE_CHECKING, Text, Union

if TYPE_CHECKING:
    from .payloads import Channel as ChannelPayload
    from .state import State

class Channel:
    def __init__(self, data: ChannelPayload, state: State):
        self.state = state
        self.id = data["_id"]
        self.channel_type = data["channel_type"]

class SavedMessageChannel(Channel):
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

class DMChannel(Channel):
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

class GroupDMChannel(Channel):
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

class TextChannel(Channel):
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

class VoiceChannel(Channel):
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

def channel_factory(data: ChannelPayload) -> type[Channel]:
    # Literal["SavedMessage", "DirectMessage", "Group", "TextChannel", "VoiceChannel"]
    channel_type = data["channel_type"]
    if channel_type == "SavedMessage":
        return SavedMessageChannel
    elif channel_type == "DirectMessage":
        return DMChannel
    elif channel_type == "Group":
        return GroupDMChannel
    elif channel_type == "TextChannel":
        return TextChannel
    elif channel_type == "VoiceChannel":
        return VoiceChannel
    else:
        raise Exception
