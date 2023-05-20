from __future__ import annotations

import io
from typing import Optional, Union, cast

__all__ = ("File",)

class File:
    """Respresents a file about to be uploaded to revolt

    Parameters
    -----------
    file: Union[str, bytes]
        The name of the file or the content of the file in bytes, text files will be need to be encoded
    filename: Optional[str]
        The filename of the file when being uploaded, this will default to the name of the file if one exists
    spoiler: bool
        Determines if the file will be a spoiler, this prefexes the filename with `SPOILER_`
    """
    __slots__ = ("f", "spoiler", "filename")

    def __init__(self, file: Union[str, bytes], *, filename: Optional[str] = None, spoiler: bool = False):
        self.f: io.BufferedIOBase

        if isinstance(file, str):
            self.f = open(file, "rb")
        else:
            self.f = io.BytesIO(file)

        if filename is None and isinstance(file, str):
            filename = cast(Optional[str], self.f.name)

        self.spoiler: bool = spoiler or (bool(filename) and filename.startswith("SPOILER_"))

        if self.spoiler and (filename and not filename.startswith("SPOILER_")):
            filename = f"SPOILER_{filename}"

        self.filename: str | None = filename
