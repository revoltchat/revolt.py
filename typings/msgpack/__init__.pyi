from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Tuple

from typing_extensions import Protocol

class _FileLike(Protocol):
    def read(self, n: int) -> bytes: ...

def unpackb(
    packed: bytes,
    file_like: Optional[_FileLike] = ...,
    read_size: int = ...,
    use_list: bool = ...,
    raw: bool = ...,
    timestamp: int = ...,
    strict_map_key: bool = ...,
    object_hook: Optional[Callable[[Dict[Any, Any]], Any]] = ...,
    object_pairs_hook: Optional[Callable[[List[Tuple[Any, Any]]], Any]] = ...,
    list_hook: Optional[Callable[[List[Any]], Any]] = ...,
    unicode_errors: Optional[str] = ...,
    max_buffer_size: int = ...,
    ext_hook: Callable[[int, bytes], Any] = ...,
    max_str_len: int = ...,
    max_bin_len: int = ...,
    max_array_len: int = ...,
    max_map_len: int = ...,
    max_ext_len: int = ...,
) -> Any: ...

def packb(
    o: Any,
    default: Optional[Callable[[Any], Any]] = ...,
    use_single_float: bool = ...,
    autoreset: bool = ...,
    use_bin_type: bool = ...,
    strict_types: bool = ...,
    datetime: bool = ...,
    unicode_errors: Optional[str] = ...,
) -> bytes: ...
