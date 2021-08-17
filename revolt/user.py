from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import State
    from .payloads import User as UserPayload

class User:
    def __init__(self, data: UserPayload, state: State):
        self.state = state
        self.id = data["_id"]
        self.name = data["username"]
        
        bot = data.get("bot")
        if bot:
            self.bot = True
            self.owner = bot["owner"]
        else:
            self.bot = False
            self.owner = None

        self.badges = data.get("badges", 0)
        self.online = data.get("online", False)
        self.flags = data.get("flags", 0)

        # avatar
        # relations
        # relationship
