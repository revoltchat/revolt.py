from __future__ import annotations

from .messageable import Messageable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Channel as ChannelPayload
    from .state import State

class Channel:
    """Base class for all channels
    
    Attributes
    -----------
    id: :class:`str`
        The id of the channel
    channel_type: Literal['SavedMessage', 'DirectMessage', 'Group', 'TextChannel', 'VoiceChannel']
        The type of the channel
    server: Optional[:class:`Server`]
        The server the channel is part of
    """
    def __init__(self, data: ChannelPayload, state: State):
        self.state = state
        self.id = data["_id"]
        self.channel_type = data["channel_type"]
        self.server = None

class SavedMessageChannel(Channel, Messageable):
    """The Saved Message Channel"""
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

class DMChannel(Channel, Messageable):
    """A DM channel"""
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

class GroupDMChannel(Channel, Messageable):
    """A group DM channel"""
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

class TextChannel(Channel, Messageable):
    """A text channel"""
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)
        Messageable.__init__(self, state)

class PartialTextChannel(Messageable):
    """A partial text channel, this will appear when the channel isnt cached"""
    def __init__(self, channel_id: str, state: State):
        super().__init__(state)

        self.id = channel_id        
        self.name = "Unknown Channel"
        self.channel_type = "TextChannel"
        self.server = None

class VoiceChannel(Channel):
    """A voice channel"""
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

def channel_factory(data: ChannelPayload, state) -> Channel:
    if data["channel_type"] == "SavedMessage":
        return SavedMessageChannel(data, state)
    elif data["channel_type"] == "DirectMessage":
        return DMChannel(data, state)
    elif data["channel_type"] == "Group":
        return GroupDMChannel(data, state)
    elif data["channel_type"] == "TextChannel":
        return TextChannel(data, state)
    elif data["channel_type"] == "VoiceChannel":
        return VoiceChannel(data, state)
    else:
        raise Exception
