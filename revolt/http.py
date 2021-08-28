from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING, Literal
import aiohttp

from .errors import HTTPError, ServerError
from .file import File

try:
    import ujson as _json
except ImportError:
    import json as _json

if TYPE_CHECKING:
    import aiohttp
    from .payloads import ApiInfo, Autumn as AutumnPayload, Message as MessagePayload, Embed as EmbedPayload
    from .file import File

class HttpClient:
    def __init__(self, session: aiohttp.ClientSession, token: str, api_url: str, api_info: ApiInfo):
        self.session = session
        self.token = token
        self.api_url = api_url
        self.api_info = api_info

    async def request(self, method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"], route: str, *, files: Optional[list[File]] = None, json: Optional[dict] = None) -> Any:
        url = f"{self.api_url}{route}"
        
        kwargs = {}
        
        headers = {
            "User-Agent": "Revolt.py https://github.com/Zomatree/revolt.py",
            "x-bot-token": self.token
        }

        if json:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = _json.dumps(json)

        kwargs["headers"] = headers

        async with self.session.request(method, url, **kwargs) as resp:
            response = _json.loads(await resp.text())
    
        resp_code = resp.status

        if 200 <= resp_code <= 300:
            return response
        elif resp_code == 400:
            raise HTTPError

    async def upload_file(self, file: File, tag: str) -> AutumnPayload:
        url = f"{self.api_info['features']['autumn']['url']}/{tag}"

        headers = {
            "User-Agent": "Revolt.py https://github.com/Zomatree/revolt.py"
        }

        form = aiohttp.FormData()
        form.add_field("file", file.f.read(), filename=file.filename)

        async with self.session.post(url, data=form, headers=headers) as resp:
            response: AutumnPayload = _json.loads(await resp.text())

        resp_code = resp.status

        if resp_code == 400:
            raise HTTPError(response)
        elif 500 <= resp_code <= 600:
            raise ServerError
        else:
            return response

    async def send_message(self, channel: str, content: Optional[str], embeds: Optional[list[EmbedPayload]], attachments: Optional[list[File]]) -> MessagePayload:
        json = {}
        
        if content:
            json["content"] = content
        
        if embeds:
            json["embeds"] = embeds

        if attachments:
            attachment_ids = []

            for attachment in attachments:
                data = await self.upload_file(attachment, "attachments")
                attachment_ids.append(data["id"])
                
            json["attachments"] = attachment_ids

        return await self.request("POST", "/channels/{channel}/messages", json=json)
