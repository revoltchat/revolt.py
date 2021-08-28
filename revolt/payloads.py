from typing import Literal, Type, TypedDict, Union

class ApiFeature(TypedDict):
    enabled: bool
    url: str

class VosoFeature(ApiFeature):
    ws: str

class Features(TypedDict):
    email: bool
    invite_only: bool
    captcha: ApiFeature
    autumn: ApiFeature
    january: ApiFeature
    voso: VosoFeature

class ApiInfo(TypedDict):
    revolt: str
    features: Features
    ws: str
    app: str
    vapid: str

class BasePayload(TypedDict):
    type: str

class AuthenticatePayload(BasePayload):
    token: str

class UserBot(TypedDict):
    owner: str

class SizedMetadata(TypedDict):
    type: Literal["Image", "Video"]
    height: int
    width: int

class SimpleMetadata(TypedDict):
    type: Literal["File", "Text", "Audio"]

FileMetadata = Union[SizedMetadata, SimpleMetadata]

class File(TypedDict):
    _id: str
    tag: str
    size: int
    filename: str
    metadata: FileMetadata
    content_type: str

class Status(TypedDict, total=False):
    text: str
    presence: Literal["Busy", "Idle", "Invisible", "Online"]

class _OptionalUser(TypedDict, total=False):
    avatar: File
    relations: list
    badges: int
    status: Status
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

class Embed(TypedDict):
    pass  # TODO

class Message(_OptionalMessage):
    _id: str
    channel: str
    author: str
    content: Union[str, UserAddContent, UserRemoveContent, UserJoinedContent, UserLeftContent, UserKickedContent, UserBanned, ChannelRenameContent, ChannelDescriptionChangeContent, ChannelIconChanged]
    embeds: list[Embed]

class _NonceChannel(TypedDict, total=False):
    nonce: str

class BaseChannel(TypedDict):
    _id: str

class SavedMessages(_NonceChannel, BaseChannel):
    user: str
    channel_type: Literal["SavedMessage"]

class DirectMessage(_NonceChannel, BaseChannel):
    active: bool
    recipients: list[str]
    last_message: Message
    channel_type: Literal["DirectMessage"]

class _GroupOptional(TypedDict):
    icon: File
    permissions: int
    description: str

class Group(_NonceChannel, _GroupOptional, BaseChannel):
    recipients: list[str]
    name: str
    owner: str
    channel_type: Literal["Group"]

class _TextChannelOptional(TypedDict, total=False):
    icon: File
    default_permissions: int
    role_permissions: int

class TextChannel(_NonceChannel, _TextChannelOptional, BaseChannel):
    server: str
    name: str
    description: str
    last_message: Message
    channel_type: Literal["TextChannel"]

class _VoiceChannelOptional(TypedDict, total=False):
    icon: File
    default_permissions: int
    role_permissions: int

class VoiceChannel(_NonceChannel, _TextChannelOptional, BaseChannel):
    server: str
    name: str
    description: str
    channel_type: Literal["VoiceChannel"]

Channel = Union[SavedMessages, DirectMessage, Group, TextChannel, VoiceChannel]

class ReadyEventPayload(BasePayload):
    users: list[User]
    servers: list[Server]
    channels: list[Channel]

class MessageEventPayload(BasePayload, Message):
    pass

class Autumn(TypedDict):
    id: str

class _MemberOptional(TypedDict, total=False):
    nickname: str
    avatar: File
    roles: list[str]

class Member(_MemberOptional):
    _id: str

Permission = tuple[int, int]

class _RoleOptional(TypedDict, total=False):
    colour: str
    hoist: bool
    rank: int

class Role(_RoleOptional):
    name: str
    permissions: Permission
