from __future__ import annotations

from typing import Literal, TypedDict, Union

__all__ = ("File",)

class SizedMetadata(TypedDict):
    type: Literal["Image", "Video"]
    height: int
    width: int

class SimpleMetadata(TypedDict):
    type: Literal["File", "Text", "Audio"]

FileMetadata = Union[SizedMetadata, SimpleMetadata]

class File(TypedDict):
    _id: str
    tag: str
    size: int
    filename: str
    metadata: FileMetadata
    content_type: str
