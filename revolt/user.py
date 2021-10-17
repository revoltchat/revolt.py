from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Optional

from .asset import Asset
from .enums import PresenceType, RelationshipType

if TYPE_CHECKING:
    from .state import State
    from .types import User as UserPayload
    from .types import UserRelation


__all__ = ("User",)

class Relation(NamedTuple):
    """A namedtuple representing a relation between the bot and a user"""
    type: RelationshipType
    user: User

class Status(NamedTuple):
    """A namedtuple representing a users status"""
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
    relations: list[:class:`Relation`]
        A list of the users relations
    relationship: Optional[:class:`RelationshipType`]
        The relationship between the user and the bot
    status: Optional[:class:`Status`]
        The users status
    """
    __flattern_attributes__ = ("id", "name", "bot", "owner_id", "badges", "online", "flags", "avatar", "relations", "relationship", "status")
    __slots__ = (*__flattern_attributes__, "state")

    def __init__(self, data: UserPayload, state: State):
        self.state = state
        self.id = data["_id"]
        self.name = data["username"]
        
        bot = data.get("bot")
        if bot:
            self.bot = True
            self.owner_id = bot["owner"]
        else:
            self.bot = False
            self.owner_id = None

        self.badges = data.get("badges", 0)
        self.online = data.get("online", False)
        self.flags = data.get("flags", 0)

        avatar = data.get("avatar")
        self.avatar = Asset(avatar, state) if avatar else None

        relations = []

        for relation in data.get("relations", []):
            user = state.get_user(relation["_id"])
            if user:
                relations.append(Relation(RelationshipType(relation["status"]), user))
        self.relations = relations

        relationship = data.get("relationship")
        self.relationship = RelationshipType(relationship) if relationship else None

        status = data.get("status")
        if status:
            presence = status.get("presence")
            self.status = Status(status.get("text"), PresenceType(presence) if presence else None) if status else None
        else:
            self.status = None

    @property
    def owner(self) -> Optional[User]:
        owner_id = self.owner_id

        if not owner_id:
            return

        return self.state.get_user(owner_id)
