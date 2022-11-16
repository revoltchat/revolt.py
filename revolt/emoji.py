from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .utils import Ulid

if TYPE_CHECKING:
    from .state import State
    from .types import Emoji as EmojiPayload
    from .server import Server

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
        self.state = state

        self.id = payload["_id"]
        self.author_id = payload["creator_id"]
        self.name = payload["name"]
        self.animated = payload.get("animated", False)
        self.nsfw = payload.get("nsfw", False)
        self.server_id: Optional[str] = payload["parent"].get("id")

    async def delete(self):
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
