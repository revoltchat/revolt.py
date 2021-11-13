from typing import Annotated
from .errors import BadBoolArgument

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
