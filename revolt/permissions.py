from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Permission as PermissionTuple


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

class _Permission:

    __slots__ = ("_value",)
    
    def __init__(self, value: int):
        self._value = value

    def __or__(self, p: _Permission):
        self._value |= p._value
        return self

    def __and__(self, p: _Permission):
        self._value &= p._value
        return self

    def __invert__(self):
        self._value = ~self._value
        return self
    
    def __add__(self, p: _Permission):
        # For example we have a bit array `0011` representing permissions
        # To allow a permission we would convert the bit for that permission from 0 to 1
        # Let's say we want to allow permissions with bit array `0101` 
        # Our desired result is `0111` which can be achieved by simple OR (A+B)
        return self | p
    
    def __sub__(self, p: _Permission):
        # For example we have a bit array `0011` representing permissions
        # To deny a permission we would convert the bit for that permission from 1 to 0
        # Let's say we want to deny permissions with bit array `0101` 
        # Our desired result is `0010` which can be achieved by Selective Clear Algorithm (A.B')
        return self & ~p

    def __lt__(self, p: _Permission):
        return self._value < p._value
    
    def __gt__(self, p: _Permission):
        return self._value > p._value

    def __eq__(self, p: _Permission):
        return self._value == p._value

    def __repr__(self):
        return f"{self.__class__.__name__}<{self._value:032b}>"

    def _check(self, bit_pos: int):
        # To check if a permission is present we would need to compare the bit for that position in our bit array
        # For example if we have permission `0100` and we need to check if it is present in our bit array `0101`
        # We need to compare the 3rd bit from the left, so we shift it 2 places (n-1) and perform AND with 1
        # If the result is 1 the bit was 1 and the permission is present
        return (self._value >> bit_pos) & 1 == 1

class ChannelPermissions(_Permission):
    """Represents the channel permissions for a role as seen in channel settings."""
    
    __slots__ = ()

    @property
    def value(self) -> int:
        return self._value

    @classmethod
    def none(cls) -> ChannelPermissions:
        return cls(0)

    @classmethod
    def all(cls) -> ChannelPermissions:
        # channel permissions here do not have manage messages permission
        return cls(0b00000000000000000000000011111011)

    @classmethod
    def view(cls) -> ChannelPermissions:
        return cls(0b00000000000000000000000000000001)

    # view permission is always present and therefore is included in every permission below

    @classmethod
    def send_message(cls) -> ChannelPermissions:
        return cls(0b00000000000000000000000000000011)

    @classmethod
    def manage_channel(cls) -> ChannelPermissions:
        return cls(0b00000000000000000000000000001001)

    @classmethod
    def voice_call(cls) -> ChannelPermissions:
        return cls(0b00000000000000000000000000010001)

    @classmethod
    def invite_others(cls) -> ChannelPermissions:
        return cls(0b00000000000000000000000000100001)

    @classmethod
    def embed_links(cls) -> ChannelPermissions:
        return cls(0b00000000000000000000000001000001)

    @classmethod
    def upload_files(cls) -> ChannelPermissions:
        return cls(0b00000000000000000000000010000001)

    @property
    def can_view(self) -> bool:
        return self._check(0)

    @property
    def can_send_message(self) -> bool:
        return self._check(1)

    @property
    def can_manage_channel(self) -> bool:
        return self._check(3)

    @property
    def can_voice_call(self) -> bool:
        return self._check(4)

    @property
    def can_invite_others(self) -> bool:
        return self._check(5)

    @property
    def can_embed_links(self) -> bool:
        return self._check(6)

    @property
    def can_upload_files(self) -> bool:
        return self._check(7)

class ServerPermissions:
    """Represents the server permissions for a role as seen in server settings."""
    
    __slots__ = ("_server_perms", "_channel_perms", )

    def __init__(self, server_perms: int, channel_perms: int) -> None:
        self._server_perms = _Permission(server_perms)
        self._channel_perms = _Permission(channel_perms)

    def __add__(self, p: ServerPermissions) -> ServerPermissions:
        self._server_perms += p._server_perms
        self._channel_perms += p._channel_perms       
        return self
    
    def __sub__(self, p: ServerPermissions) -> ServerPermissions:
        self._server_perms -= p._server_perms
        self._channel_perms -= p._channel_perms       
        return self

    def __lt__(self, p: ServerPermissions) -> bool:
        return self._server_perms < p._server_perms and self._channel_perms < p._channel_perms
    
    def __gt__(self, p: ServerPermissions) -> bool:
        return self._server_perms > p._server_perms and self._channel_perms > p._channel_perms

    def __eq__(self, p: ServerPermissions) -> bool:
        return self._server_perms == p._server_perms and self._channel_perms == p._channel_perms

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<Server: {self._server_perms._value:032b} Channel: {self._channel_perms._value:032b}>"

    @property
    def value(self) -> PermissionTuple:
        return self._server_perms._value, self._channel_perms._value

    @classmethod
    def none(cls) -> ServerPermissions:
        return cls(0, 0)

    @classmethod
    def all(cls) -> ServerPermissions:
        # channel permissions here do not have manage channel permission
        return cls(0b00000000000000001111000000111111, 0b00000000000000000000000011110111)

    # view server and view channel are always present and therefore are included in every permission below
    # server permissions

    @classmethod
    def view_server(cls) -> ServerPermissions:
        return cls(0b00000000000000000000000000000001, 1)

    @classmethod
    def manage_roles(cls) -> ServerPermissions:
        return cls(0b00000000000000000000000000000011, 1)

    @classmethod
    def manage_channels(cls) -> ServerPermissions:
        return cls(0b00000000000000000000000000000101, 1)

    @classmethod
    def manage_server(cls) -> ServerPermissions:
        return cls(0b00000000000000000000000000001001, 1)

    @classmethod
    def kick_members(cls) -> ServerPermissions:
        return cls(0b00000000000000000000000000010001, 1)

    @classmethod
    def ban_members(cls) -> ServerPermissions:
        return cls(0b00000000000000000000000000100001, 1)

    @classmethod
    def change_nicknames(cls) -> ServerPermissions:
        return cls(0b00000000000000000001000000000001, 1)

    @classmethod
    def manage_nicknames(cls) -> ServerPermissions:
        return cls(0b00000000000000000010000000000001, 1)

    @classmethod
    def change_avatar(cls) -> ServerPermissions:
        return cls(0b00000000000000000100000000000001, 1)

    @classmethod
    def remove_avatars(cls) -> ServerPermissions:
        return cls(0b00000000000000001000000000000001, 1)

    @property
    def can_view_server(self) -> bool:
        return self._server_perms._check(0)

    @property
    def can_manage_roles(self) -> bool:
        return self._server_perms._check(1)

    @property
    def can_manage_channels(self) -> bool:
        return self._server_perms._check(2)

    @property
    def can_manage_server(self) -> bool:
        return self._server_perms._check(3)

    @property
    def can_kick_members(self) -> bool:
        return self._server_perms._check(4)

    @property
    def can_ban_members(self) -> bool:
        return self._server_perms._check(5)

    @property
    def can_change_nicknames(self) -> bool:
        return self._server_perms._check(12)

    @property
    def can_manage_nicknames(self) -> bool:
        return self._server_perms._check(13)

    @property
    def can_change_avatar(self) -> bool:
        return self._server_perms._check(14)

    @property
    def can_remove_avatars(self) -> bool:
        return self._server_perms._check(15)

    # channel permissions

    @classmethod
    def view_channels(cls) -> ServerPermissions:
        return cls(1, 0b00000000000000000000000000000001)

    @classmethod
    def send_message(cls) -> ServerPermissions:
        return cls(1, 0b00000000000000000000000000000011)

    @classmethod
    def manage_messages(cls) -> ServerPermissions:
        return cls(1, 0b00000000000000000000000000000101)

    @classmethod
    def voice_call(cls) -> ServerPermissions:
        return cls(1, 0b00000000000000000000000000010001)

    @classmethod
    def invite_others(cls) -> ServerPermissions:
        return cls(1, 0b00000000000000000000000000100001)

    @classmethod
    def embed_links(cls) -> ServerPermissions:
        return cls(1, 0b00000000000000000000000001000001)

    @classmethod
    def upload_files(cls) -> ServerPermissions:
        return cls(1, 0b00000000000000000000000010000001)

    @property
    def can_view_channel(self) -> bool:
        return self._channel_perms._check(0)

    @property
    def can_send_message(self) -> bool:
        return self._channel_perms._check(1)

    @property
    def can_manage_messages(self) -> bool:
        return self._channel_perms._check(2)

    @property
    def can_voice_call(self) -> bool:
        return self._channel_perms._check(4)

    @property
    def can_invite_others(self) -> bool:
        return self._channel_perms._check(5)

    @property
    def can_embed_links(self) -> bool:
        return self._channel_perms._check(6)

    @property
    def can_upload_files(self) -> bool:
        return self._channel_perms._check(7)
