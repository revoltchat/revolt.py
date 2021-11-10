from typing import Annotated

class ConverterError(Exception):
    """Raised when a converter fails"""

class BadBoolArgument(ConverterError):
    """Raised when the bool converter fails"""

IntConverter = Annotated[int, lambda arg, _: int(arg)]

def bool_converter(arg: str, _):
    lowered = arg.lower()
    if lowered in  ["yes", "true", "ye", "y", "1", "on", "enable"]:
        return True
    elif lowered in ('no', 'n', 'false', 'f', '0', 'disable', 'off'):
        return False
    else:
        raise BadBoolArgument(lowered)

BoolConverter = Annotated[bool, bool_converter]
