from __future__ import annotations

from .flags import Flags, flag_value


__all__ = (
    "ChannelPermissions",
    "ServerPermissions"
)

# Channel permissions
#
#   View = 0b00000000000000000000000000000001           // 1
#   SendMessage = 0b00000000000000000000000000000010    // 2
#   ManageMessages = 0b00000000000000000000000000000100 // 4
#   ManageChannel = 0b00000000000000000000000000001000  // 8
#   VoiceCall = 0b00000000000000000000000000010000      // 16
#   InviteOthers = 0b00000000000000000000000000100000   // 32
#   EmbedLinks = 0b00000000000000000000000001000000     // 64
#   UploadFiles = 0b00000000000000000000000010000000    // 128


# Server permissions
#
#   View = 0b00000000000000000000000000000001            // 1
#   ManageRoles = 0b00000000000000000000000000000010     // 2
#   ManageChannels = 0b00000000000000000000000000000100  // 4
#   ManageServer = 0b00000000000000000000000000001000    // 8
#   KickMembers = 0b00000000000000000000000000010000     // 16
#   BanMembers = 0b00000000000000000000000000100000      // 32

#   ChangeNickname = 0b00000000000000000001000000000000  // 4096
#   ManageNicknames = 0b00000000000000000010000000000000 // 8192
#   ChangeAvatar = 0b00000000000000000100000000000000    // 16382
#   RemoveAvatars = 0b00000000000000001000000000000000   // 32768

class ChannelPermissions(Flags):
    """Represents the channel permissions for a role as seen in channel settings."""

    @classmethod
    def none(cls) -> ChannelPermissions:
        return cls._from_value(0)

    @classmethod
    def all(cls) -> ChannelPermissions:
        return cls._from_value(0b11111011)

    @classmethod
    def view(cls) -> ChannelPermissions:
        return cls._from_value(0b1)

    @classmethod
    def send_message(cls) -> ChannelPermissions:
        return cls._from_value(0b11)

    @classmethod
    def manage_channel(cls) -> ChannelPermissions:
        return cls._from_value(0b1001)

    @classmethod
    def voice_call(cls) -> ChannelPermissions:
        return cls._from_value(0b10001)

    @classmethod
    def invite_others(cls) -> ChannelPermissions:
        return cls._from_value(0b100001)

    @classmethod
    def embed_links(cls) -> ChannelPermissions:
        return cls._from_value(0b1000001)

    @classmethod
    def upload_files(cls) -> ChannelPermissions:
        return cls._from_value(0b10000001)

    @flag_value
    def can_view() -> int:
        return 1 << 0

    @flag_value
    def can_send_message() -> int:
        return 1 << 1

    @flag_value
    def can_manage_channel() -> int:
        return 1 << 3

    @flag_value
    def can_voice_call() -> int:
        return 1 << 4

    @flag_value
    def can_invite_others() -> int:
        return 1 << 5

    @flag_value
    def can_embed_links() -> int:
        return 1 << 6

    @flag_value
    def can_upload_files() -> int:
        return 1 << 7

class ServerPermissions(Flags):
    """Represents the server permissions for a role as seen in server settings."""

    @classmethod
    def none(cls) -> ServerPermissions:
        return cls._from_value(0)

    @classmethod
    def all(cls) -> ServerPermissions:
        return cls._from_value(0b1111000000111111)

    @flag_value
    def view_server() -> int:
        return 1 << 0

    @flag_value
    def manage_roles() -> int:
        return 1 << 1

    @flag_value
    def manage_channels() -> int:
        return 1 << 2

    @flag_value
    def manage_server() -> int:
        return 1 << 3

    @flag_value
    def kick_members() -> int:
        return 1 << 4

    @flag_value
    def ban_members() -> int:
        return 1 << 5

    @flag_value
    def change_nicknames() -> int:
        return 1 << 12

    @flag_value
    def manage_nicknames() -> int:
        return 1 << 13

    @flag_value
    def change_avatar() -> int:
        return 1 << 14

    @flag_value
    def remove_avatars() -> int:
        return 1 << 15
