from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import File as FilePayload
    from .state import State
    from io import IOBase

class Asset:
    """Represents a file on revolt
    
    Attributes
    -----------
    id: str
        The id of the asset
    tag: str
        The tag of the asset, this corrasponds to where the asset is used
    size: int
        Amount of bytes in the file
    filename: str
        The name of the file
    height: Optional[int]
        The height of the file if it is an image or video
    width: Optional[int]
        The width of the file if it is an image or video
    content_type: str
        The content type of the file 
    """
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
        """Reads the files content into bytes"""
        ...

    async def save(self, fp: IOBase):
        """Reads the files content and saves it to a file
        
        Parameters
        -----------
        fp: IOBase
            The file to write too.
        """
        fp.write(await self.read())
