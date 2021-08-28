from typing import Optional, Union

import io
import os

class File:
    def __init__(self, file: Union[str, bytes], *, filename: Optional[str] = None, spoiler: bool = False):
        if isinstance(file, str):
            self.f = open(file, "rb")
        elif isinstance(file, bytes):
            self.f = io.BytesIO(file)

        if filename is None and isinstance(file, str):
            filename = self.f.name
            
        if spoiler or (filename and filename.startswith("SPOILER_")):
            self.spoiler = True
        else:
            self.spoiler = False

        if self.spoiler and (filename and not filename.startswith("SPOILER_")):
            filename = f"SPOILER_{filename}"

        self.filename = filename
