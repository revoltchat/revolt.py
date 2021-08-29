from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import State
    from .types import User as UserPayload

class User:
    """Represents a user
    
    Attributes
    -----------
    id: :class:`str`
        The users id
    name: :class:`str`
        The users name
    bot: :class:`bool`
        Whether or not the user is a bot
    owner: Optional[:class:`User`]
        The bot's owner if the user is a bot
    badges: :class:`int`
        The users badges
    online: :class:`bool`
        Whether or not the user is online
    flags: :class:`int`
        The user flags
    """
    __flattern_attributes__ = ("id", "name", "bot", "owner", "badges", "online", "flags")

    def __init__(self, data: UserPayload, state: State):
        self.state = state
        self.id = data["_id"]
        self.name = data["username"]
        
        bot = data.get("bot")
        if bot:
            self.bot = True
            self.owner = state.get_user(bot["owner"])
        else:
            self.bot = False
            self.owner = None

        self.badges = data.get("badges", 0)
        self.online = data.get("online", False)
        self.flags = data.get("flags", 0)

        # avatar
        # relations
        # relationship
