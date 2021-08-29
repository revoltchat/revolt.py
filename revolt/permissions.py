from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Permission as PermissionTuple

class Permissions:
    def __init__(self, permission_tuple: PermissionTuple):
        ...
