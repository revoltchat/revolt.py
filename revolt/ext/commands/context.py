from __future__ import annotations

from typing import Any, Callable, Coroutine, Optional
import revolt

from .command import Command

__all__ = (
    "Context",
)

class Context:
    def __init__(self, command: Optional[Command], invoked_with: str, message: revolt.Message):
        self.command = command
        self.invoked_with = invoked_with
        self.message = message

    async def invoke(self, args: list[str]) -> Any:
        if command := self.command:
            return await command.invoke(self, args)

    async def send(self, content: Optional[str] = None, *, embeds: Optional[list[revolt.Embed]] = None, embed: Optional[revolt.Embed] = None, attachments: Optional[list[revolt.File]] = None) -> revolt.Message:
        return await self.message.channel.send(content, embeds=embeds, embed=embed, attachments=attachments)

