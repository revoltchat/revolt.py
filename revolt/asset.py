from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import AssetType
from .errors import AutumnDisabled

if TYPE_CHECKING:
    from io import IOBase

    from .state import State
    from .types import File as FilePayload


__all__ = ("Asset",)

class Asset:
    """Represents a file on revolt
    
    Attributes
    -----------
    id: :class:`str`
        The id of the asset
    tag: :class:`str`
        The tag of the asset, this corrasponds to where the asset is used
    size: :class:`int`
        Amount of bytes in the file
    filename: :class:`str`
        The name of the file
    height: Optional[:class:`int`]
        The height of the file if it is an image or video
    width: Optional[:class:`int`]
        The width of the file if it is an image or video
    content_type: :class:`str`
        The content type of the file
    type: :class:`AssetType`
        The type of asset it is
    """
    __slots__ = ("state", "id", "tag", "size", "filename", "content_type", "width", "height", "type")
    
    def __init__(self, data: FilePayload, state: State):
        self.state = state

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
        self.type = AssetType(metadata["type"])

    async def read(self) -> bytes:
        """Reads the files content into bytes"""
        return await self.state.http.request_file(self.url)

    async def save(self, fp: IOBase):
        """Reads the files content and saves it to a file
        
        Parameters
        -----------
        fp: IOBase
            The file to write too.
        """
        fp.write(await self.read())

    @property
    def url(self) -> str:
        """Returns the url for the asset
        
        .. note:: This can error if autumn is disabled on the instance of revolt
        
        Returns
        --------
        :class:`str`
            The url

        Raises
        -------
        :class:`AutumnDisabled`
            Raises if autumn is disabled
        
        """
        enabled = self.state.api_info["features"]["autumn"]["enabled"]
        
        if not enabled:
            raise AutumnDisabled

        base_url = self.state.api_info["features"]["autumn"]["url"]

        return f"{base_url}/{self.tag}/{self.id}"
