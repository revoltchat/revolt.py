from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Optional

from .asset import Asset
from .enums import RelationshipType, PresenceType

if TYPE_CHECKING:
    from .state import State
    from .types import User as UserPayload, UserRelation

class Relation(NamedTuple):
    type: RelationshipType
    user: Optional["User"]

class Status(NamedTuple):
    text: Optional[str]
    presence: Optional[PresenceType]

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
    avatar: :class:`Asset`
        The users avatar if they have one
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

        avatar = data.get("avatar")
        self.avatar = Asset(avatar, state) if avatar else None

        self.relations = [Relation(RelationshipType(relation["status"]), state.get_user(relation["_id"])) for relation in data.get("relations", [])]
        relationship = data.get("relationship")
        self.relationship = RelationshipType(relationship) if relationship else None

        status = data.get("status")
        if status:
            presence = status.get("presence")
            self.status = Status(status.get("text"), PresenceType(presence) if presence else None) if status else None
        else:
            self.status = None
