from __future__ import annotations

import re
from typing import TYPE_CHECKING, Annotated, TypeVar

import ulid
from revolt import Category, Channel, Member, User, utils

from .context import Context
from .errors import (BadBoolArgument, CategoryConverterError,
                     ChannelConverterError, MemberConverterError, ServerOnly,
                     UserConverterError)

if TYPE_CHECKING:
    from .client import CommandsClient

T = TypeVar("T")

__all__: tuple[str, ...] = ("id_converter", "int_converter", "bool_converter", "category_converter", "channel_converter", "user_converter", "member_converter", "IdConverter", "IntConverter", "BoolConverter", "CategoryConverter", "UserConverter", "MemberConverter", "ChannelConverter", "Greedy")

channel_regex: re.Pattern[str] = re.compile("<#([A-z0-9]{26})>")
user_regex: re.Pattern[str] = re.compile("<@([A-z0-9]{26})>")

ClientT = TypeVar("ClientT", bound="CommandsClient")

def bool_converter(arg: str, _: Context[ClientT]) -> bool:
    lowered = arg.lower()
    if lowered in  ("yes", "true", "ye", "y", "1", "on", "enable"):
        return True
    elif lowered in ("no", "false", "n", "f", "0", "off", "disabled"):
        return False
    else:
        raise BadBoolArgument(lowered)

def category_converter(arg: str, context: Context[ClientT]) -> Category:
    if not context.server_id:
        raise ServerOnly

    try:
        return context.server.get_category(arg)
    except LookupError:
        try:
            return utils.get(context.server.categories, name=arg)
        except LookupError:
            raise CategoryConverterError(arg)

def channel_converter(arg: str, context: Context[ClientT]) -> Channel:
    if not context.server_id:
        raise ServerOnly

    if (match := channel_regex.match(arg)):
        arg = match.group(1)

    try:
        return context.server.get_channel(arg)
    except LookupError:
        try:
            return utils.get(context.server.channels, name=arg)
        except LookupError:
            raise ChannelConverterError(arg)

def user_converter(arg: str, context: Context[ClientT]) -> User:
    if (match := user_regex.match(arg)):
        arg = match.group(1)

    try:
        return context.client.get_user(arg)
    except LookupError:
        try:
            parts = arg.split("#")

            if len(parts) == 1:
                return (
                    utils.get(context.client.users, original_name=arg)
                    or utils.get(context.client.users, display_name=arg)
                )
            elif len(parts) == 2:
                return (
                    utils.get(context.client.users, original_name=parts[0], discriminator=parts[1])
                    or utils.get(context.client.users, display_name=parts[0], discriminator=parts[1])
                )
            else:
                raise LookupError

        except LookupError:
            raise UserConverterError(arg)

def member_converter(arg: str, context: Context[ClientT]) -> Member:
    if not context.server_id:
        raise ServerOnly

    if (match := user_regex.match(arg)):
        arg = match.group(1)

    try:
        return context.server.get_member(arg)
    except LookupError:
        try:
            parts = arg.split("#")

            if len(parts) == 1:
                return (
                    utils.get(context.server.members, original_name=arg)
                    or utils.get(context.server.members, display_name=arg)
                )
            elif len(parts) == 2:
                return (
                    utils.get(context.server.members, original_name=parts[0], discriminator=parts[1])
                    or utils.get(context.server.members, display_name=parts[0], discriminator=parts[1])
                )
            else:
                raise LookupError

        except LookupError:
            raise MemberConverterError(arg)

def int_converter(arg: str, context: Context[ClientT]) -> int:
    return int(arg)

def id_converter(arg: str, context: Context[ClientT]) -> ulid.ULID:
    if len(arg) != 26:
        raise ValueError("An ID was not provided.")
    
    try:
        return ulid.parse(arg)
    except Exception as err:
        raise ValueError("An invalid ID was provided.") from err

IdConverter = Annotated[ulid.ULID, id_converter]
IntConverter = Annotated[int, int_converter]
BoolConverter = Annotated[bool, bool_converter]
CategoryConverter = Annotated[Category, category_converter]
UserConverter = Annotated[User, user_converter]
MemberConverter = Annotated[Member, member_converter]
ChannelConverter = Annotated[Channel, channel_converter]

Greedy = Annotated[list[T], "_revolt_greedy_marker"]