from __future__ import annotations

from typing import TYPE_CHECKING

from .utils import Ulid

if TYPE_CHECKING:
    from .server import Server
    from .state import State
    from .types import Emoji as EmojiPayload

__all__ = ("Emoji",)

class Emoji(Ulid):
    """Represents a custom emoji.

    Attributes
    -----------
    id: :class:`str`
        The id of the emoji
    author_id: :class:`str`
        The id of the of user who created the emoji
    name: :class:`str`
        The name of the emoji
    animated: :class:`bool`
        Whether or not the emoji is animated
    nsfw: :class:`bool`
        Whether or not the emoji is nsfw
    server_id: Optional[:class:`str`]
        The server id this emoji belongs to, if any
    """
    def __init__(self, payload: EmojiPayload, state: State):
        self.state: State = state

        self.id: str = payload["_id"]
        self.author_id: str = payload["creator_id"]
        self.name: str = payload["name"]
        self.animated: bool = payload.get("animated", False)
        self.nsfw: bool = payload.get("nsfw", False)
        self.server_id: str | None = payload["parent"].get("id")

    async def delete(self) -> None:
        """Deletes the emoji."""
        await self.state.http.delete_emoji(self.id)

    @property
    def server(self) -> Server:
        """Returns the server this emoji is part of

        Returns
        --------
        :class:`Server`
            The Server this emoji is part of
        """
        return self.state.get_server(self.server_id)  # type: ignore
