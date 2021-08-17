from typing import Literal, TypedDict, Union

class ApiInfo(TypedDict):
    revolt: str
    features: dict
    ws: str
    app: str
    vapid: str

class BasePayload(TypedDict):
    type: str

class AuthenticatePayload(BasePayload):
    token: str

class UserBot(TypedDict):
    owner: str

class _FileMetadataOptional(TypedDict, total=False):
    width: int
    height: int

class FileMetadata(_FileMetadataOptional):
    type: Literal["File", "Text", "Audio", "Image", "Video"]

class File(TypedDict):
    _id: str
    tag: str
    size: int
    filename: str
    metadata: FileMetadata
    content_type: str

class _OptionalUser(TypedDict, total=False):
    avatar: File
    relations: list
    badges: int
    status: ...
    relationship: Literal["Blocked", "BlockedOther", "Friend", "Incoming", "None", "Outgoing", "User"]
    online: bool
    flags: int
    bot: UserBot

class User(_OptionalUser):
    _id: str
    username: str

class Server(TypedDict):
    _id: str

class UserAddContent(TypedDict):
    id: str
    by: str

class UserRemoveContent(TypedDict):
    id: str
    by: str

class UserJoinedContent(TypedDict):
    id: str
    by: str

class UserLeftContent(TypedDict):
    id: str

class UserKickedContent(TypedDict):
    id: str

class UserBanned(TypedDict):
    id: str

class ChannelRenameContent(TypedDict):
    name: str
    by: str

class ChannelDescriptionChangeContent(TypedDict):
    by: str

class ChannelIconChanged(TypedDict):
    by: str

class _OptionalMessage(TypedDict):
    attachments: list[File]

class Message(_OptionalMessage):
    _id: str
    channel: str
    author: str
    content: Union[str, UserAddContent, UserRemoveContent, UserJoinedContent, UserLeftContent, UserKickedContent, UserBanned, ChannelRenameContent, ChannelDescriptionChangeContent, ChannelIconChanged]

class _OptionalChannel(TypedDict, total=False):
    user: str
    nonce: str
    active: str
    recipients: list[str]
    last_message: Message
    name: str
    owner: str
    description: str
    icon: File

class Channel(_OptionalChannel):
    _id: str
    channel_type: Literal["SavedMessage", "DirectMessage", "Group", "TextChannel", "VoiceChannel"]

class ReadyPayload(BasePayload):
    users: list[User]
    servers: list[Server]
    channels: list[Channel]

class MessageEventPayload(BasePayload):
    pass
