from __future__ import annotations

from .messageable import Messageable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Channel as ChannelPayload
    from .state import State

class Channel:
    def __init__(self, data: ChannelPayload, state: State):
        self.state = state
        self.id = data["_id"]
        self.channel_type = data["channel_type"]
        self.server = None

class SavedMessageChannel(Channel, Messageable):
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

class DMChannel(Channel, Messageable):
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

class GroupDMChannel(Channel, Messageable):
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

class TextChannel(Channel, Messageable):
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)
        Messageable.__init__(self, state)

class PartialTextChannel(Messageable):
    def __init__(self, channel_id: str, state: State):
        super().__init__(state)

        self.id = channel_id        
        self.name = "Unknown Channel"
        self.channel_type = "TextChannel"
        self.server = None

class VoiceChannel(Channel):
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

def channel_factory(data: ChannelPayload) -> type[Channel]:
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
