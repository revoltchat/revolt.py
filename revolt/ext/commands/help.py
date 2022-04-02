from __future__ import annotations
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING, TypedDict, Union, Optional
from typing_extensions import NotRequired
from itertools import groupby

from .utils import evaluate_parameters
from .command import Command, command
from .client import CommandsClient
from .context import Context
from .group import Group

if TYPE_CHECKING:
    from .cog import Cog
    from revolt import SendableEmbed, File, MessageReply, Message, Messageable

__all__ = ("MessagePayload", "HelpCommand", "DefaultHelpCommand", "help_command_impl")

class MessagePayload(TypedDict):
    content: str
    embed: NotRequired[SendableEmbed]
    embeds: NotRequired[list[SendableEmbed]]
    attachments: NotRequired[list[File]]
    replies: NotRequired[list[MessageReply]]


class HelpCommand(ABC):
    @abstractmethod
    async def create_bot_help(self, context: Context, commands: dict[Optional[Cog], list[Command]]) -> Union[str, SendableEmbed, MessagePayload]:
        raise NotImplementedError

    @abstractmethod
    async def create_command_help(self, context: Context, command: Command) -> Union[str, SendableEmbed, MessagePayload]:
        raise NotImplementedError

    @abstractmethod
    async def create_group_help(self, context: Context, group: Group) -> Union[str, SendableEmbed, MessagePayload]:
        raise NotImplementedError

    @abstractmethod
    async def create_cog_help(self, context: Context, cog: Cog) -> Union[str, SendableEmbed, MessagePayload]:
        raise NotImplementedError

    async def send_help_command(self, context: Context, message_payload: MessagePayload) -> Message:
        return await context.send(**message_payload)

    async def filter_commands(self, context: Context, commands: list[Command]) -> list[Command]:
        filtered: list[Command] = []

        for command in commands:
            try:
                if await context.can_run(command):
                    filtered.append(command)
            except Exception:
                pass

        return filtered

    async def group_commands(self, context: Context, commands: list[Command]) -> dict[Optional[Cog], list[Command]]:
        cogs = {}

        for command in commands:
            cogs.setdefault(command.cog, []).append(command)

        return cogs

    async def handle_message(self, context: Context, message: Message):
        pass

    async def get_channel(self, context: Context) -> Messageable:
        return context

    @abstractmethod
    async def handle_no_command_found(self, context: Context, name: str):
        raise NotImplementedError

    @abstractmethod
    async def handle_no_cog_found(self, context: Context, name: str):
        raise NotImplementedError


class DefaultHelpCommand(HelpCommand):
    def __init__(self, default_cog_name: str = "No Cog"):
        self.default_cog_name = default_cog_name

    async def create_bot_help(self, context: Context, commands: dict[Optional[Cog], list[Command]]) -> Union[str, SendableEmbed, MessagePayload]:
        lines = ["```"]

        for cog, cog_commands in commands.items():
            cog_lines = []
            cog_lines.append(f"{cog.qualified_name if cog else self.default_cog_name}:")

            for command in cog_commands:
                cog_lines.append(f"  {command.name} - {command.short_description or 'No description'}")

            lines.append("\n".join(cog_lines))

        lines.append("```")
        return "\n".join(lines)

    async def create_cog_help(self, context: Context, cog: Cog) -> Union[str, SendableEmbed, MessagePayload]:
        lines = ["```"]

        lines.append(f"{cog.qualified_name}:")

        for command in cog.commands:
            lines.append(f"  {command.name} - {command.short_description or 'No description'}")

        lines.append("```")
        return "\n".join(lines)

    async def create_command_help(self, context: Context, command: Command) -> Union[str, SendableEmbed, MessagePayload]:
        lines = ["```"]

        lines.append(f"{command.name}:")
        lines.append(f"  Usage: {command.get_usage()}")

        if command.aliases:
            lines.append(f"  Aliases: {', '.join(command.aliases)}")


        if command.description:
            lines.append(command.description)

        lines.append("```")
        return "\n".join(lines)

    async def create_group_help(self, context: Context, group: Group) -> Union[str, SendableEmbed, MessagePayload]:
        lines = ["```"]

        lines.append(f"{group.name}:")
        lines.append(f"  Usage: {group.get_usage()}")

        if group.aliases:
            lines.append(f"  Aliases: {', '.join(group.aliases)}")

        if group.description:
            lines.append(group.description)

        for command in group.commands:
            lines.append(f"  {command.name} - {command.short_description or 'No description'}")

        lines.append("```")
        return "\n".join(lines)

    async def handle_no_command_found(self, context: Context, name: str):
        channel = await self.get_channel(context)
        await channel.send(f"Command `{name}` not found.")

    async def handle_no_cog_found(self, context: Context, name: str):
        channel = await self.get_channel(context)
        await channel.send(f"Cog `{name}` not found.")


class HelpCommandImpl(Command):
    def __init__(self, client: CommandsClient):
        self.client = client
        super().__init__(callback=lambda _, context, *args: help_command_impl(self.client, context, *args), name="help", aliases=[])
        self.description = "Shows help for a command, cog or the entire bot"


async def help_command_impl(self: CommandsClient, context: Context, *arguments: str):
    filtered_commands = await context.client.help_command.filter_commands(context, self.commands)
    commands = await self.help_command.group_commands(context, filtered_commands)

    if not arguments:
        payload = await self.help_command.create_bot_help(context, commands)
    else:
        command_name = arguments[0]

        try:
            command = self.get_command(command_name)
        except KeyError:
            cog = self.cogs.get(command_name)
            if cog:
                payload = await self.help_command.create_cog_help(context, cog)
            else:
                return await self.help_command.handle_no_command_found(context, command_name)
        else:
            if isinstance(command, Group):
                payload = await self.help_command.create_group_help(context, command)
            else:
                payload = await self.help_command.create_command_help(context, command)

    msg_payload: MessagePayload

    if isinstance(payload, str):
        msg_payload = {"content": payload}
    elif isinstance(payload, SendableEmbed):
        msg_payload = {"embed": payload, "content": " "}
    else:
        msg_payload = payload

    await self.help_command.send_help_command(context, msg_payload)
