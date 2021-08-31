from __future__ import annotations

from typing import Any, Coroutine, Optional, TYPE_CHECKING, Literal, TypeVar, Union
import aiohttp
import ulid

from .errors import HTTPError, ServerError
from .file import File

try:
    import ujson as _json
except ImportError:
    import json as _json

if TYPE_CHECKING:
    import aiohttp
    from .types import (
        ApiInfo, Autumn as AutumnPayload, Message as MessagePayload, Embed as EmbedPayload, GetServerMembers, User as UserPayload,
        Server, Member, UserProfile, ServerInvite, ServerBans, Channel, DMChannel, TextChannel, VoiceChannel, Role)
    from .file import File

T = TypeVar("T")
Request = Coroutine[Any, Any, T]

class HttpClient:
    def __init__(self, session: aiohttp.ClientSession, token: str, api_url: str, api_info: ApiInfo):
        self.session = session
        self.token = token
        self.api_url = api_url
        self.api_info = api_info

    async def request(self, method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"], route: str, *, json: Optional[dict] = None, nonce: bool = True) -> Any:
        url = f"{self.api_url}{route}"

        kwargs = {}
        
        headers = {
            "User-Agent": "Revolt.py https://github.com/Zomatree/revolt.py",
            "x-bot-token": self.token
        }

        if json:
            headers["Content-Type"] = "application/json"

            if nonce:
                json["nonce"] = ulid.new().str

            kwargs["data"] = _json.dumps(json)

        kwargs["headers"] = headers

        async with self.session.request(method, url, **kwargs) as resp:
            text = await resp.text()
            if text:
                response = _json.loads(await resp.text())
            else:
                response = text

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

        return await self.request("POST", f"/channels/{channel}/messages", json=json)

    async def request_file(self, url: str) -> bytes:
        async with self.session.get(url) as resp:
            return await resp.content.read()

    def fetch_user(self, user_id: str) -> Request[UserPayload]:
        return self.request("GET", f"/users/{user_id}")

    def fetch_profile(self, user_id: str) -> Request[UserProfile]:
        return self.request("GET", f"/users/{user_id}/profile")

    def fetch_default_avatar(self, user_id: str) -> Request[bytes]:
        return self.request_file(f"{self.api_url}/users/{user_id}/default_avatar")
    
    def fetch_dm_channels(self) -> Request[list[Channel]]:
        return self.request("GET", "/users/dms")

    def open_dm(self, user_id: str) -> Request[DMChannel]:
        return self.request("GET", f"/users/{user_id}/dm")

    def fetch_channel(self, channel_id: str) -> Request[Channel]:
        return self.request("GET", f"/channels/{channel_id}")

    def close_channel(self, channel_id: str) -> Request[None]:
        return self.request("DELETE", f"/channels/{channel_id}")

    def fetch_server(self, server_id: str) -> Request[Server]:
        return self.request("GET", f"/servers/{server_id}")

    def delete_leave_server(self, server_id: str) -> Request[None]:
        return self.request("DELETE", f"/servers/{server_id}")

    def create_channel(self, server_id: str, channel_type: Literal["Text", "Voice"], name: str, description: Optional[str]) -> Request[Union[TextChannel, VoiceChannel]]:
        payload = {
            "type": channel_type,
            "name": name
        }

        if description:
            payload["description"] = description

        return self.request("POST", f"/servers/{server_id}/channels", json=payload)

    def fetch_server_invites(self, server_id: str) -> Request[list[ServerInvite]]:
        return self.request("GET", f"/servers/{server_id}/invites")

    def fetch_member(self, server_id: str, member_id: str) -> Request[Member]:
        return self.request("GET", f"/servers/{server_id}/members/{member_id}")

    def kick_member(self, server_id: str, member_id: str) -> Request[None]:
        return self.request("DELETE", f"/servers/{server_id}/members/{member_id}")

    def fetch_members(self, server_id: str) -> Request[GetServerMembers]:
        return self.request("GET", f"/servers/{server_id}/members")

    def ban_member(self, server_id: str, member_id: str, reason: Optional[str]) -> Request[GetServerMembers]:
        payload = {"reason": reason} if reason else None

        return self.request("PUT", f"/servers/{server_id}/bans/{member_id}", json=payload, nonce=False)

    def unban_member(self, server_id: str, member_id: str) -> Request[None]:
        return self.request("DELETE", f"/servers/{server_id}/bans/{member_id}")
    
    def fetch_bans(self, server_id: str) -> Request[ServerBans]:
        return self.request("GET", f"/servers/{server_id}/bans")

    def set_role_permissions(self, server_id: str, role_id: str, server_permissions: int, channel_permissions: int) -> Request[None]:
        payload = {
            "server": server_permissions,
            "channel": channel_permissions
        }

        return self.request("PUT", f"/servers/{server_id}/permissions/{role_id}", json=payload, nonce=False)
    
    def set_default_permissions(self, server_id: str, server_permissions: int, channel_permissions: int) -> Request[None]:
        payload = {
            "server": server_permissions,
            "channel": channel_permissions
        }

        return self.request("PUT", f"/servers/{server_id}/permissions/default", json=payload, nonce=False)

    def create_role(self, server_id: str, name: str) -> Request[Role]:
        return self.request("POST", f"/servers/{server_id}/roles", json={"name": name}, nonce=False)

    def delete_role(self, server_id: str, role_id: str) -> Request[None]:
        return self.request("DELETE", f"/servers/{server_id}/roles/{role_id}")
