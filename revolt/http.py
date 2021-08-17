from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import aiohttp
    from .payloads import ApiInfo

class HttpClient:
    def __init__(self, session: aiohttp.ClientSession, token: str, api_url: str, api_info: ApiInfo):
        self.session = session
        self.token = token
        self.api_info = api_info

