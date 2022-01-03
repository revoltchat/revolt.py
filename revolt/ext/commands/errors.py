from revolt import RevoltError

__all__ = (
    "CommandError",
    "CommandNotFound",
    "NoClosingQuote",
    "CheckError",
    "NotBotOwner",
    "NotServerOwner",
    "ServerOnly",
    "ConverterError",
    "InvalidLiteralArgument",
    "BadBoolArgument",
    "CategoryConverterError",
    "ChannelConverterError",
    "UserConverterError",
    "MemberConverterError",
)

class CommandError(RevoltError):
    """base error for all command's related errors"""

class CommandNotFound(CommandError):
    """Raised when a command isnt found.

    Parameters
    -----------
    command_name: :class:`str`
        The name of the command that wasnt found
    """
    __slots__ = ("command_name",)

    def __init__(self, command_name: str):
        self.command_name = command_name

class NoClosingQuote(CommandError):
    """Raised when there is no closing quote for a command argument"""

class CheckError(CommandError):
    """Raised when a check fails for a command"""

class NotBotOwner(CheckError):
    """Raised when the `is_bot_owner` check fails"""

class NotServerOwner(CheckError):
    """Raised when the `is_server_owner` check fails"""

class ServerOnly(CheckError):
    """Raised when a check requires the command to be ran in a server"""

class ConverterError(CommandError):
    """Base class for all converter errors"""

class InvalidLiteralArgument(ConverterError):
    """Raised when the argument is not a valid literal argument"""

class BadBoolArgument(ConverterError):
    """Raised when the bool converter fails"""

class CategoryConverterError(ConverterError):
    """Raised when the Category conveter fails"""
    def __init__(self, argument: str):
        self.argument = argument

class ChannelConverterError(ConverterError):
    """Raised when the Channel conveter fails"""
    def __init__(self, argument: str):
        self.argument = argument

class UserConverterError(ConverterError):
    """Raised when the Category conveter fails"""
    def __init__(self, argument: str):
        self.argument = argument

class MemberConverterError(ConverterError):
    """Raised when the Category conveter fails"""
    def __init__(self, argument: str):
        self.argument = argument
