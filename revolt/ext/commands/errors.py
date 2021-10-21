__all__ = (
    "CommandNotFound",
)

class CommandNotFound(Exception):
    """Raised when a command isnt found.
    
    Parameters
    -----------
    command_name: :class:`str`
        The name of the command that wasnt found
    """
    __slots__ = ("command_name",)

    def __init__(self, command_name: str):
        self.command_name = command_name
