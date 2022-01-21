from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Optional, Union

from .asset import Asset, PartialAsset
from .channel import DMChannel
from .enums import PresenceType, RelationshipType
from .flags import UserBadges
from .messageable import Messageable

if TYPE_CHECKING:
    from .state import State
    from .types import File
    from .types import Status as StatusPayload
    from .types import User as UserPayload


__all__ = ("User",)

class Relation(NamedTuple):
    """A namedtuple representing a relation between the bot and a user"""
    type: RelationshipType
    user: User

class Status(NamedTuple):
    """A namedtuple representing a users status"""
    text: Optional[str]
    presence: Optional[PresenceType]

class UserProfile(NamedTuple):
    """A namedtuple representing a users profile"""
    content: Optional[str]
    background: Optional[Asset]

class User(Messageable):
    """Represents a user
    
    Attributes
    -----------
    id: :class:`str`
        The users id
    bot: :class:`bool`
        Whether or not the user is a bot
    owner: Optional[:class:`User`]
        The bot's owner if the user is a bot
    badges: :class:`UserBadges`
        The users badges
    online: :class:`bool`
        Whether or not the user is online
    flags: :class:`int`
        The user flags
    relations: list[:class:`Relation`]
        A list of the users relations
    relationship: Optional[:class:`RelationshipType`]
        The relationship between the user and the bot
    status: Optional[:class:`Status`]
        The users status
    dm_channel: Optional[:class:`DMChannel`]
        The dm channel between the client and the user, this will only be set if the client has dm'ed the user or :meth:`User.open_dm` was run
    """
    __flattern_attributes__ = ("id", "bot", "owner_id", "badges", "online", "flags", "relations", "relationship", "status", "masquerade_avatar", "masquerade_name", "original_name", "original_avatar", "profile", "dm_channel")
    __slots__ = (*__flattern_attributes__, "state")

    def __init__(self, data: UserPayload, state: State):
        self.state = state
        self.id = data["_id"]
        self.original_name = data["username"]
        self.dm_channel = None

        bot = data.get("bot")
        if bot:
            self.bot = True
            self.owner_id = bot["owner"]
        else:
            self.bot = False
            self.owner_id = None

        self.badges = UserBadges._from_value(data.get("badges", 0))
        self.online = data.get("online", False)
        self.flags = data.get("flags", 0)

        avatar = data.get("avatar")
        self.original_avatar = Asset(avatar, state) if avatar else None

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

        self.profile: Optional[UserProfile] = None

        self.masquerade_avatar: Optional[PartialAsset] = None
        self.masquerade_name: Optional[str] = None

    async def _get_channel_id(self):
        if not self.dm_channel:
            payload = await self.state.http.open_dm(self.id)
            self.dm_channel = DMChannel(payload, self.state)

        return self.id

    @property
    def owner(self) -> Optional[User]:
        owner_id = self.owner_id

        if not owner_id:
            return

        return self.state.get_user(owner_id)

    @property
    def name(self) -> str:
        """:class:`str` The name the user is displaying, this includes there orginal name and masqueraded name"""
        return self.masquerade_name or self.original_name

    @property
    def avatar(self) -> Union[Asset, PartialAsset, None]:
        """Optional[:class:`Asset`] The avatar the member is displaying, this includes there orginal avatar and masqueraded avatar"""
        return self.masquerade_avatar or self.original_avatar

    def _update(self, *, status: Optional[StatusPayload] = None, profile_content: Optional[str] = None, profile_background: Optional[File] = None, avatar: Optional[File] = None, online: Optional[bool] = None):
        if status:
            presence = status.get("presence")
            self.status = Status(status.get("text"), PresenceType(presence) if presence else None)

        if profile_background:
            self.profile = UserProfile(self.profile.content if self.profile else None, Asset(profile_background, self.state))

        if profile_content:
            self.profile = UserProfile(profile_content, self.profile.background if self.profile else None)

        if avatar:
            self.original_avatar = Asset(avatar, self.state)

        if online:
            self.online = online

    async def default_avatar(self) -> bytes:
        """Returns the default avatar for this user

        Returns
        --------
        :class:`bytes`
            The bytes of the image
        """
        return await self.state.http.fetch_default_avatar(self.id)

    async def fetch_profile(self) -> UserProfile:
        """Fetches the user's profile

        Returns
        --------
        :class:`UserProfile`
            The user's profile
        """
        payload = await self.state.http.fetch_profile(self.id)

        if file := payload.get("background"):
            background = Asset(file, self.state)
        else:
            background = None

        return UserProfile(payload.get("content"), background)
