from revolt import RevoltError

__all__ = (
    "CommandError",
    "CommandNotFound",
    "NoClosingQuote",
    "CheckError",
    "NotBotOwner",
    "NotServerOwner",
    "ServerOnly",
    "MissingPermissionsError",
    "ConverterError",
    "InvalidLiteralArgument",
    "BadBoolArgument",
    "CategoryConverterError",
    "ChannelConverterError",
    "IdConverterError",
    "UserConverterError",
    "MemberConverterError",
    "UnionConverterError",
    "MissingSetup",
    "CommandOnCooldown"
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
        self.command_name: str = command_name

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

class MissingPermissionsError(CheckError):
    """Raised when a check requires permissions the user does not have

    Attributes
    -----------
    permissions: :class:`dict[str, bool]`
        The permissions which the user did not have
    """

    def __init__(self, permissions: dict[str, bool]):
        self.permissions = permissions

class ConverterError(CommandError):
    """Base class for all converter errors"""

class InvalidLiteralArgument(ConverterError):
    """Raised when the argument is not a valid literal argument"""

class BadBoolArgument(ConverterError):
    """Raised when the bool converter fails"""

class IdConverterError(ConverterError):
    """Raised when the ID converter fails"""

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

class UnionConverterError(ConverterError):
    """Raised when all converters in a union fails"""
    def __init__(self, argument: str):
        self.argument = argument

class MissingSetup(CommandError):
    """Raised when an extension is missing the `setup` function"""

class CommandOnCooldown(CommandError):
    """Raised when a command is on cooldown

    Attributes
    -----------
    retry_after: :class:`float`
        How long the user must wait until the cooldown resets
    """

    __slots__ = ("retry_after",)

    def __init__(self, retry_after: float):
        self.retry_after: float = retry_after