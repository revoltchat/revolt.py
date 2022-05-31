from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from typing_extensions import Self

from .types.permissions import Overwrite
from .flags import Flags, flag_value

__all__ = ("Permissions", "PermissionsOverwrite")

class Permissions(Flags):
    @flag_value
    def manage_channel() -> int:
        return 1 << 0

    @flag_value
    def manage_server() -> int:
        return 1 << 1

    @flag_value
    def manage_permissions() -> int:
        return 1 << 2

    @flag_value
    def manage_role() -> int:
        return 1 << 3

    @flag_value
    def kick_members() -> int:
        return 1 << 6

    @flag_value
    def ban_members() -> int:
        return 1 << 7

    @flag_value
    def timeout_members() -> int:
        return 1 << 8

    @flag_value
    def asign_roles() -> int:
        return 1 << 9

    @flag_value
    def change_nickname() -> int:
        return 1 << 10

    @flag_value
    def manage_nicknames() -> int:
        return 1 << 11

    @flag_value
    def change_avatars() -> int:
        return 1 << 12

    @flag_value
    def remove_avatars() -> int:
        return 1 << 13

    @flag_value
    def view_channel() -> int:
        return 1 << 20

    @flag_value
    def read_message_history() -> int:
        return 1 << 21

    @flag_value
    def send_messages() -> int:
        return 1 << 22

    @flag_value
    def manage_messages() -> int:
        return 1 << 23

    @flag_value
    def manage_webhooks() -> int:
        return 1 << 24

    @flag_value
    def invite_others() -> int:
        return 1 << 25

    @flag_value
    def send_embeds() -> int:
        return 1 << 26

    @flag_value
    def upload_files() -> int:
        return 1 << 27

    @flag_value
    def masquerade() -> int:
        return 1 << 28

    @flag_value
    def connect() -> int:
        return 1 << 30

    @flag_value
    def speak() -> int:
        return 1 << 31

    @flag_value
    def video() -> int:
        return 1 << 32

    @flag_value
    def mute_members() -> int:
        return 1 << 33

    @flag_value
    def deafen_members() -> int:
        return 1 << 34

    @flag_value
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

class PermissionsOverwrite:
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

    def __setattr__(self, key: str, value: Any):
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
