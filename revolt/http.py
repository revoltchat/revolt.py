from __future__ import annotations

from typing import (TYPE_CHECKING, Any, Coroutine, Literal, Optional, TypeVar,
                    Union, overload)

import aiohttp
import ulid


from .errors import Forbidden, HTTPError, ServerError
from .file import File

try:
    import ujson as _json
except ImportError:
    import json as _json

if TYPE_CHECKING:
    import aiohttp

    from .enums import SortType
    from .file import File
    from .types import Autumn as AutumnPayload
    from .types import Emoji as EmojiPayload
    from .types import Interactions as InteractionsPayload
    from .types import Masquerade as MasqueradePayload
    from .types import Member as MemberPayload
    from .types import Message as MessagePayload
    from .types import SendableEmbed as SendableEmbedPayload
    from .types import User as UserPayload
    from .types import (Server, ServerBans, TextChannel, UserProfile, VoiceChannel, Member, Invite, ApiInfo, Channel, SavedMessages,
                        DMChannel, EmojiParent, GetServerMembers, GroupDMChannel, MessageReplyPayload, MessageWithUserData, PartialInvite, Role)

__all__ = ("HttpClient",)

T = TypeVar("T")
Request = Coroutine[Any, Any, T]

class HttpClient:
    __slots__ = ("session", "token", "api_url", "api_info", "auth_header")

    def __init__(self, session: aiohttp.ClientSession, token: str, api_url: str, api_info: ApiInfo, bot: bool = True):
        self.session: aiohttp.ClientSession = session
        self.token: str = token
        self.api_url: str = api_url
        self.api_info: ApiInfo = api_info
        self.auth_header: str = "x-bot-token" if bot else "x-session-token"

    async def request(self, method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"], route: str, *, json: Optional[dict[str, Any]] = None, nonce: bool = True, params: Optional[dict[str, Any]] = None) -> Any:
        url = f"{self.api_url}{route}"

        kwargs = {}

        headers = {
            "User-Agent": "Revolt.py (https://github.com/revoltchat/revolt.py)",
            self.auth_header: self.token
        }

        if json:
            headers["Content-Type"] = "application/json"

            if nonce:
                json["nonce"] = ulid.new().str # type: ignore

            kwargs["data"] = _json.dumps(json)

        kwargs["headers"] = headers

        if params:
            kwargs["params"] = params

        async with self.session.request(method, url, **kwargs) as resp:
            text = await resp.text()
            if text:
                try:
                    response = _json.loads(await resp.text())
                except ValueError:
                    raise HTTPError(f"Invalid json response:\n{text}") from None
            else:
                response = text

        resp_code = resp.status

        if 200 <= resp_code <= 300:
            return response
        elif resp_code == 401:
            raise Forbidden("401: Missing Permissions")
        else:
            raise HTTPError(resp_code)

    async def upload_file(self, file: File, tag: Literal["attachments", "avatars", "backgrounds", "icons", "banners", "emojis"]) -> AutumnPayload:
        url = f"{self.api_info['features']['autumn']['url']}/{tag}"

        headers = {
            "User-Agent": "Revolt.py (https://github.com/revoltchat/revolt.py)"
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

    async def send_message(self, channel: str, content: Optional[str], embeds: Optional[list[SendableEmbedPayload]], attachments: Optional[list[File]], replies: Optional[list[MessageReplyPayload]], masquerade: Optional[MasqueradePayload], interactions: Optional[InteractionsPayload]) -> MessagePayload:
        json: dict[str, Any] = {}

        if content:
            json["content"] = content

        if embeds:
            json["embeds"] = embeds

        if attachments:
            attachment_ids: list[str] = []

            for attachment in attachments:
                data = await self.upload_file(attachment, "attachments")
                attachment_ids.append(data["id"])

            json["attachments"] = attachment_ids

        if replies:
            json["replies"] = replies

        if masquerade:
            json["masquerade"] = masquerade

        if interactions:
            json["interactions"] = interactions

        return await self.request("POST", f"/channels/{channel}/messages", json=json)

    def edit_message(self, channel: str, message: str, content: Optional[str], embeds: Optional[list[SendableEmbedPayload]] = None) -> Request[None]:
        json = {}

        if content is not None:
            json["content"] = content

        if embeds is not None:
            json["embeds"] = embeds

        return self.request("PATCH", f"/channels/{channel}/messages/{message}", json=json)

    def delete_message(self, channel: str, message: str) -> Request[None]:
        return self.request("DELETE", f"/channels/{channel}/messages/{message}")

    def fetch_message(self, channel: str, message: str) -> Request[MessagePayload]:
        return self.request("GET", f"/channels/{channel}/messages/{message}")

    @overload
    def fetch_messages(
        self,
        channel: str,
        sort: SortType,
        *,
        limit: Optional[int] = ...,
        before: Optional[str] = ...,
        after: Optional[str] = ...,
        nearby: Optional[str] = ...,
        include_users: Literal[False] = ...
    ) -> Request[list[MessagePayload]]:
        ...

    @overload
    def fetch_messages(
        self,
        channel: str,
        sort: SortType,
        *,
        limit: Optional[int] = ...,
        before: Optional[str] = ...,
        after: Optional[str] = ...,
        nearby: Optional[str] = ...,
        include_users: Literal[True] = ...
    ) -> Request[MessageWithUserData]:
        ...

    def fetch_messages(
        self,
        channel: str,
        sort: SortType,
        *,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        nearby: Optional[str] = None,
        include_users: bool = False
    ) -> Request[Union[list[MessagePayload], MessageWithUserData]]:

        json: dict[str, Any] = {"sort": sort.value, "include_users": str(include_users)}

        if limit:
            json["limit"] = limit

        if before:
            json["before"] = before

        if after:
            json["after"] = after

        if nearby:
            json["nearby"] = nearby

        return self.request("GET", f"/channels/{channel}/messages", params=json)

    @overload
    def search_messages(
        self,
        channel: str,
        query: str,
        *,
        limit: Optional[int] = ...,
        before: Optional[str] = ...,
        after: Optional[str] = ...,
        sort: Optional[SortType] = ...,
        include_users: Literal[False] = ...
    ) -> Request[list[MessagePayload]]:
        ...

    @overload
    def search_messages(
        self,
        channel: str,
        query: str,
        *,
        limit: Optional[int] = ...,
        before: Optional[str] = ...,
        after: Optional[str] = ...,
        sort: Optional[SortType] = ...,
        include_users: Literal[True] = ...
    ) -> Request[MessageWithUserData]:
        ...

    def search_messages(
        self,
        channel: str,
        query: str,
        *,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        sort: Optional[SortType] = None,
        include_users: bool = False
    ) -> Request[Union[list[MessagePayload], MessageWithUserData]]:

        json: dict[str, Any] = {"query": query, "include_users": include_users}

        if limit:
            json["limit"] = limit

        if before:
            json["before"] = before

        if after:
            json["after"] = after

        if sort:
            json["sort"] = sort.value

        return self.request("POST", f"/channels/{channel}/search", json=json)

    async def request_file(self, url: str) -> bytes:
        async with self.session.get(url) as resp:
            return await resp.content.read()

    def fetch_user(self, user_id: str) -> Request[UserPayload]:
        return self.request("GET", f"/users/{user_id}")

    def fetch_profile(self, user_id: str) -> Request[UserProfile]:
        return self.request("GET", f"/users/{user_id}/profile")

    def fetch_default_avatar(self, user_id: str) -> Request[bytes]:
        return self.request_file(f"{self.api_url}/users/{user_id}/default_avatar")

    def fetch_dm_channels(self) -> Request[list[Union[DMChannel, GroupDMChannel]]]:
        return self.request("GET", "/users/dms")

    def open_dm(self, user_id: str) -> Request[DMChannel | SavedMessages]:
        return self.request("GET", f"/users/{user_id}/dm")

    def fetch_channel(self, channel_id: str) -> Request[Channel]:
        return self.request("GET", f"/channels/{channel_id}")

    def close_channel(self, channel_id: str) -> Request[None]:
        return self.request("DELETE", f"/channels/{channel_id}")

    def fetch_server(self, server_id: str) -> Request[Server]:
        return self.request("GET", f"/servers/{server_id}")

    def delete_leave_server(self, server_id: str) -> Request[None]:
        return self.request("DELETE", f"/servers/{server_id}")

    @overload
    def create_channel(self, server_id: str, channel_type: Literal["Text"], name: str, description: Optional[str]) -> Request[TextChannel]:
        ...

    @overload
    def create_channel(self, server_id: str, channel_type: Literal["Voice"], name: str, description: Optional[str]) -> Request[VoiceChannel]:
        ...

    def create_channel(self, server_id: str, channel_type: Literal["Text", "Voice"], name: str, description: Optional[str]) -> Request[Union[TextChannel, VoiceChannel]]:
        payload = {
            "type": channel_type,
            "name": name
        }

        if description:
            payload["description"] = description

        return self.request("POST", f"/servers/{server_id}/channels", json=payload)

    def fetch_server_invites(self, server_id: str) -> Request[list[PartialInvite]]:
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

    def create_role(self, server_id: str, name: str) -> Request[Role]:
        return self.request("POST", f"/servers/{server_id}/roles", json={"name": name}, nonce=False)

    def delete_role(self, server_id: str, role_id: str) -> Request[None]:
        return self.request("DELETE", f"/servers/{server_id}/roles/{role_id}")

    def fetch_invite(self, code: str) -> Request[Invite]:
        return self.request("GET", f"/invites/{code}")

    def delete_invite(self, code: str) -> Request[None]:
        return self.request("DELETE", f"/invites/{code}")

    def edit_channel(self, channel_id: str, remove: list[str] | None, values: dict[str, Any]) -> Request[None]:
        if remove:
            values["remove"] = remove

        return self.request("PATCH", f"/channels/{channel_id}", json=values)

    def edit_role(self, server_id: str, role_id: str, remove: list[str] | None, values: dict[str, Any]) -> Request[None]:
        if remove:
            values["remove"] = remove

        return self.request("PATCH", f"/servers/{server_id}/roles/{role_id}", json=values)

    async def edit_self(self, remove: list[str] | None, values: dict[str, Any]) -> Request[None]:
        if remove:
            values["remove"] = remove

        if avatar := values.get("avatar"):
            asset = await self.upload_file(avatar, "avatars")
            values["avatar"] = asset["id"]

        if profile := values.get("profile"):
            if background := profile.background():
                asset = await self.upload_file(background, "backgrounds")
                profile["background"] = asset["id"]

        return await self.request("PATCH", "/users/@me", json=values)

    def set_guild_channel_default_permissions(self, channel_id: str, allow: int, deny: int) -> Request[None]:
        return self.request("PUT", f"/channels/{channel_id}/permissions/default", json={"permissions": {"allow": allow, "deny": deny}})

    def set_guild_channel_role_permissions(self, channel_id: str, role_id: str, allow: int, deny: int) -> Request[None]:
        return self.request("PUT", f"/channels/{channel_id}/permissions/{role_id}", json={"permissions": {"allow": allow, "deny": deny}})

    def set_group_channel_default_permissions(self, channel_id: str, value: int) -> Request[None]:
        return self.request("PUT", f"/channels/{channel_id}/permissions/default", json={"permissions": value})

    def set_server_role_permissions(self, server_id: str, role_id: str, allow: int, deny: int) -> Request[None]:
        return self.request("PUT", f"/servers/{server_id}/permissions/{role_id}", json={"permissions": {"allow": allow, "deny": deny}})

    def set_server_default_permissions(self, server_id: str, value: int) -> Request[None]:
        return self.request("PUT", f"/servers/{server_id}/permissions/default", json={"permissions": value})

    def add_reaction(self, channel_id: str, message_id: str, emoji: str) -> Request[None]:
        return self.request("PUT", f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}")

    def remove_reaction(self, channel_id: str, message_id: str, emoji: str, user_id: Optional[str], remove_all: bool) -> Request[None]:
        parameters = {}

        if user_id:
            parameters["user_id"] = user_id

        parameters["remove_all"] = remove_all

        return self.request("DELETE", f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}", params=parameters)

    def remove_all_reactions(self, channel_id: str, message_id: str) -> Request[None]:
        return self.request("DELETE", f"/channels/{channel_id}/messages/{message_id}/reactions")

    def delete_emoji(self, emoji_id: str) -> Request[None]:
        return self.request("DELETE", f"/custom/emoji/{emoji_id}")

    def fetch_emoji(self, emoji_id: str) -> Request[EmojiPayload]:
        return self.request("GET", f"/custom/emoji/{emoji_id}")

    async def create_emoji(self, name: str, file: File, nsfw: bool, parent: EmojiParent) -> EmojiPayload:
        asset = await self.upload_file(file, "emojis")

        return await self.request("PUT", f"/custom/emoji/{asset['id']}", json={"name": name, "parent": parent, "nsfw": nsfw})

    def edit_member(self, server_id: str, member_id: str, remove: list[str] | None, values: dict[str, Any]) -> Request[MemberPayload]:
        return self.request("PATCH", f"/servers/{server_id}/members/{member_id}", json={"remove": remove, **values})

    def delete_messages(self, channel_id: str, messages: list[str]) -> Request[None]:
        return self.request("DELETE", f"/channels/{channel_id}/messages/bulk", json={"ids": messages})
