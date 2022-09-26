from typing import TYPE_CHECKING

# typing does not understand aenum so I am pretending its stdlib enum while type checking

if TYPE_CHECKING:
    import enum
else:
    import aenum as enum


__all__ = (
    "ChannelType",
    "PresenceType",
    "RelationshipType",
    "AssetType",
    "SortType",
    "EmbedType"
)

class ChannelType(enum.Enum):
    saved_messages = "SavedMessages"
    direct_message = "DirectMessage"
    group = "Group"
    text_channel = "TextChannel"
    voice_channel = "VoiceChannel"

class PresenceType(enum.Enum):
    busy = "Busy"
    idle = "Idle"
    invisible = "Invisible"
    online = "Online"
    focus = "Focus"

class RelationshipType(enum.Enum):
    blocked = "Blocked"
    blocked_other = "BlockedOther"
    friend = "Friend"
    incoming_friend_request = "Incoming"
    none = "None"
    outgoing_friend_request = "Outgoing"
    user = "User"

class AssetType(enum.Enum):
    image = "Image"
    video = "Video"
    text = "Text"
    audio = "Audio"
    file = "File"

class SortType(enum.Enum):
    latest = "Latest"
    oldest = "Oldest"
    relevance = "Relevance"

class EmbedType(enum.Enum):
    website = "Website"
    image = "Image"
    text = "Text"
    none = "None"
