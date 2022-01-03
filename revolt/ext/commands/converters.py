from typing import Annotated
import re


from .errors import BadBoolArgument, ServerOnly, CategoryConverterError, ChannelConverterError, UserConverterError, MemberConverterError
from .context import Context

from revolt import Category, Channel, utils, User, Member

channel_regex = re.compile("<#([A-z0-9]{26})>")
user_regex = re.compile("<@([A-z0-9]{26})>")

def bool_converter(arg: str, _):
    lowered = arg.lower()
    if lowered in  ["yes", "true", "ye", "y", "1", "on", "enable"]:
        return True
    elif lowered in ('no', 'n', 'false', 'f', '0', 'disable', 'off'):
        return False
    else:
        raise BadBoolArgument(lowered)

def category_converter(arg: str, context: Context) -> Category:
    if not (server := context.server):
        raise ServerOnly

    try:
        return server.get_category(arg)
    except KeyError:
        try:
            return utils.get(server.categories, name=arg)
        except LookupError:
            raise CategoryConverterError(arg)

def channel_converter(arg: str, context: Context) -> Channel:
    if not (server := context.server):
        raise ServerOnly

    if (match := channel_regex.match(arg)):
        arg = match.group(1)

    try:
        return server.get_channel(arg)
    except KeyError:
        try:
            return utils.get(server.channels, name=arg)
        except LookupError:
            raise ChannelConverterError(arg)

def user_converter(arg: str, context: Context) -> User:
    if (match := user_converter.match(arg)):
        arg = match.group(1)

    try:
        return context.client.get_user(arg)
    except KeyError:
        try:
            return utils.get(context.client.users, name=arg)
        except LookupError:
            raise UserConverterError(arg)

def member_converter(arg: str, context: Context) -> Member:
    if not (server := context.server):
        raise ServerOnly

    if (match := user_converter.match(arg)):
        arg = match.group(1)

    try:
        return server.get_member(arg)
    except KeyError:
        try:
            return utils.get(server.members, name=arg)
        except LookupError:
            raise MemberConverterError(arg)

IntConverter = Annotated[int, lambda arg, _: int(arg)]
BoolConverter = Annotated[bool, bool_converter]
CategoryConverter = Annotated[Category, category_converter]
UserConverter = Annotated[User, user_converter]
MemberConverter = Annotated[Member, member_converter]
