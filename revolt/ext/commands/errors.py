__all__ = (
    "CommandNotFound",
)

class CommandNotFound(Exception):
    def __init__(self, command_name: str):
        self.command_name = command_name
