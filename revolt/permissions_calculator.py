from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, cast

from revolt.enums import ChannelType

from .permissions import Permissions

if TYPE_CHECKING:
    from .channel import Channel, DMChannel, GroupDMChannel, ServerChannel
    from .member import Member
    from .server import Server


def calculate_permissions(member: Member, target: Server | Channel) -> Permissions:
    if member.privileged:
        return Permissions.all()

    from .server import Server

    if isinstance(target, Server):
        if target.owner_id == member.id:
            return Permissions.all()

        permissions = target.default_permissions

        for role in member.roles:
            permissions = (permissions | role.permissions._allow) & (~role.permissions._deny)

        if member.current_timeout and member.current_timeout > datetime.now():
            permissions = permissions & Permissions.default_view_only()

        return permissions

    else:
        channel_type = target.channel_type

        if channel_type is ChannelType.saved_messages:
            return Permissions.all()

        elif channel_type is ChannelType.direct_message:
            target = cast("DMChannel", target)

            user_permissions = target.recipient.get_permissions()

            if user_permissions.send_message:
                return Permissions.default_direct_message()

            else:
                return Permissions.default_view_only()

        elif channel_type is ChannelType.group:
            target = cast("GroupDMChannel", target)

            if target.owner.id != member.id:
                return Permissions.default_direct_message()
            else:
                if target.permissions.value == 0:
                    return Permissions.default_direct_message()
                else:
                    return target.permissions

        else:
            target = cast("ServerChannel", target)
            server = target.server

            if server.owner_id == member.id:
                return Permissions.all()

            else:
                perms = calculate_permissions(member, server)
                perms = (perms | target.default_permissions._allow) & (~target.default_permissions._deny)

                for role in server.roles[::-1]:
                    if overwrite :=target.permissions.get(role.id):
                        perms = (perms | overwrite._allow) & (~overwrite._deny)

                if member.current_timeout and member.current_timeout > datetime.now():
                    perms = perms & Permissions(view_channel=True, read_message_history=True)

                return perms
