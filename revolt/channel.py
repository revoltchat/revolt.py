from __future__ import annotations

from typing import TYPE_CHECKING, cast

from .enums import ChannelType
from .messageable import Messageable

if TYPE_CHECKING:
    from .state import State
    from .types import Channel as ChannelPayload
    from .types import DMChannel as DMChannelPayload
    from .types import Group as GroupDMChannelPayload
    from .types import SavedMessages as SavedMessagesPayload
    from .types import TextChannel as TextChannelPayload
    from .user import User


__all__ = ("Channel",)

class Channel:
    """Base class for all channels
    
    Attributes
    -----------
    id: :class:`str`
        The id of the channel
    channel_type: ChannelType
        The type of the channel
    server: Optional[:class:`Server`]
        The server the channel is part of
    """
    __slots__ = ("state", "id", "channel_type", "server")
    
    def __init__(self, data: ChannelPayload, state: State):
        self.state = state
        self.id = data["_id"]
        self.channel_type = ChannelType(data["channel_type"])
        self.server = None

class SavedMessageChannel(Channel, Messageable):
    """The Saved Message Channel"""
    def __init__(self, data: SavedMessagesPayload, state: State):
        super().__init__(data, state)

class DMChannel(Channel, Messageable):
    """A DM channel"""
    def __init__(self, data: DMChannelPayload, state: State):
        super().__init__(data, state)

class GroupDMChannel(Channel, Messageable):
    __slots__ = ("recipients", "name", "owner")

    """A group DM channel"""
    def __init__(self, data: GroupDMChannelPayload, state: State):
        super().__init__(data, state)
        self.recipients = cast(list[User], list(filter(bool, [state.get_user(user_id) for user_id in data["recipients"]])))
        self.name = data["name"]
        self.owner = state.get_user(data["owner"])

class TextChannel(Channel, Messageable):
    __slots__ = ("name", "description", "last_message", "last_message_id")

    """A text channel"""
    def __init__(self, data: TextChannelPayload, state: State):
        super().__init__(data, state)
        
        self.server = state.get_server(data["server"])
        self.name = data["name"]
        self.description = data.get("description")
        
        last_message_id = data.get("last_message")
        self.last_message = state.get_message(last_message_id)
        self.last_message_id = last_message_id

class VoiceChannel(Channel):
    """A voice channel"""
    def __init__(self, data: ChannelPayload, state: State):
        super().__init__(data, state)

def channel_factory(data: ChannelPayload, state: State) -> Channel:
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
