from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from typing_extensions import Self

from .flags import Flag, Flags
from .types.permissions import Overwrite

__all__ = ("Permissions", "PermissionsOverwrite", "UserPermissions")

class UserPermissions(Flags):
    """Permissions for users"""

    @Flag
    def access() -> int:
        return 1 << 0

    @Flag
    def view_profile() -> int:
        return 1 << 1

    @Flag
    def send_message() -> int:
        return 1 << 2

    @Flag
    def invite() -> int:
        return 1 << 3

    @classmethod
    def all(cls) -> Self:
        return cls(access=True, view_profile=True, send_message=True, invite=True)

class Permissions(Flags):
    """Server permissions for members and roles"""

    @Flag
    def manage_channel() -> int:
        return 1 << 0

    @Flag
    def manage_server() -> int:
        return 1 << 1

    @Flag
    def manage_permissions() -> int:
        return 1 << 2

    @Flag
    def manage_role() -> int:
        return 1 << 3

    @Flag
    def kick_members() -> int:
        return 1 << 6

    @Flag
    def ban_members() -> int:
        return 1 << 7

    @Flag
    def timeout_members() -> int:
        return 1 << 8

    @Flag
    def asign_roles() -> int:
        return 1 << 9

    @Flag
    def change_nickname() -> int:
        return 1 << 10

    @Flag
    def manage_nicknames() -> int:
        return 1 << 11

    @Flag
    def change_avatars() -> int:
        return 1 << 12

    @Flag
    def remove_avatars() -> int:
        return 1 << 13

    @Flag
    def view_channel() -> int:
        return 1 << 20

    @Flag
    def read_message_history() -> int:
        return 1 << 21

    @Flag
    def send_messages() -> int:
        return 1 << 22

    @Flag
    def manage_messages() -> int:
        return 1 << 23

    @Flag
    def manage_webhooks() -> int:
        return 1 << 24

    @Flag
    def invite_others() -> int:
        return 1 << 25

    @Flag
    def send_embeds() -> int:
        return 1 << 26

    @Flag
    def upload_files() -> int:
        return 1 << 27

    @Flag
    def masquerade() -> int:
        return 1 << 28

    @Flag
    def connect() -> int:
        return 1 << 30

    @Flag
    def speak() -> int:
        return 1 << 31

    @Flag
    def video() -> int:
        return 1 << 32

    @Flag
    def mute_members() -> int:
        return 1 << 33

    @Flag
    def deafen_members() -> int:
        return 1 << 34

    @Flag
    def move_members() -> int:
        return 1 << 35

    @classmethod
    def all(cls) -> Self:
        return cls(0x000F_FFFF_FFFF_FFFF)

    @classmethod
    def default_view_only(cls) -> Self:
        return cls(view_channel=True, read_message_history=True)

    @classmethod
    def default(cls) -> Self:
        return cls.default_view_only() | cls(send_messages=True, invite_others=True, send_embeds=True, upload_files=True, connect=True, speak=True)

    @classmethod
    def default_direct_message(cls) -> Self:
        return cls.default_view_only() | cls(react=True, manage_channel=True)

class PermissionsOverwrite:
    """A permissions overwrite in a channel"""

    def __init__(self, allow: Permissions, deny: Permissions):
        self._allow = allow
        self._deny = deny

        for perm in Permissions.FLAG_NAMES:
            if getattr(allow, perm):
                value = True
            elif getattr(deny, perm):
                value = False
            else:
                value = None

            super().__setattr__(perm, value)

    def __setattr__(self, key: str, value: Any) -> None:
        if key in Permissions.FLAG_NAMES:
            if key is True:
                setattr(self._allow, key, True)
                super().__setattr__(key, True)

            elif key is False:
                setattr(self._deny, key, True)
                super().__setattr__(key, False)

            else:
                setattr(self._allow, key, False)
                setattr(self._deny, key, False)
                super().__setattr__(key, None)
        else:
            super().__setattr__(key, value)

    if TYPE_CHECKING:
        manage_channel: Optional[bool]
        manage_server: Optional[bool]
        manage_permissions: Optional[bool]
        manage_role: Optional[bool]
        kick_members: Optional[bool]
        ban_members: Optional[bool]
        timeout_members: Optional[bool]
        asign_roles: Optional[bool]
        change_nickname: Optional[bool]
        manage_nicknames: Optional[bool]
        change_avatars: Optional[bool]
        remove_avatars: Optional[bool]
        view_channel: Optional[bool]
        read_message_history: Optional[bool]
        send_messages: Optional[bool]
        manage_messages: Optional[bool]
        manage_webhooks: Optional[bool]
        invite_others: Optional[bool]
        send_embeds: Optional[bool]
        upload_files: Optional[bool]
        masquerade: Optional[bool]
        connect: Optional[bool]
        speak: Optional[bool]
        video: Optional[bool]
        mute_members: Optional[bool]
        deafen_members: Optional[bool]
        move_members: Optional[bool]

    def to_pair(self) -> tuple[Permissions, Permissions]:
        return self._allow, self._deny

    @classmethod
    def _from_overwrite(cls, overwrite: Overwrite) -> Self:
        allow = Permissions(overwrite["a"])
        deny = Permissions(overwrite["d"])

        return cls(allow, deny)
