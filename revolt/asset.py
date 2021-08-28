from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .payloads import File as FilePayload
    from .state import State
    from io import IOBase
class Asset:
    def __init__(self, data: FilePayload, state: State):
        self.id = data['_id']
        self.tag = data['tag']
        self.size = data['size']
        self.filename = data['filename']
        
        metadata = data['metadata']

        if metadata["type"] == "Image" or metadata["type"] == "Video":  # cant use `in` because type narrowing wont happen
            self.height = metadata["height"]
            self.width = metadata["width"]
        else:
            self.height = None
            self.width = None

        self.content_type = data["content_type"]

    async def read(self) -> bytes:
        ...

    async def save(self, fp: IOBase):
        fp.write(await self.read())
