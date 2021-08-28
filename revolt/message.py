from __future__ import annotations


from typing import TYPE_CHECKING

from .asset import Asset
from .embed import Embed
from .channel import TextChannel

if TYPE_CHECKING:
    from .state import State
    from .payloads import Message as MessagePayload

class Message:
    def __init__(self, data: MessagePayload, state: State):
        self.state = state
        
        self.id = data["_id"]
        self.content = data['content']
        self.attachments = [Asset(attachment, state) for attachment in data.get('attachments', [])]
        self.embeds = [Embed.from_dict(embed) for embed in data["embeds"]]

        self.channel = state.get_channel(data['channel'])
        self.server = self.channel and self.channel.server
        
        if isinstance(self.channel, TextChannel):
            self.author = state.get_member(self.id, data['author'])
        else:
            self.author = state.get_user(data['author'])
