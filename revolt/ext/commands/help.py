from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, Optional, TypedDict, Union, cast

from typing_extensions import NotRequired

from .cog import Cog
from .command import Command
from .context import Context
from .group import Group
from .utils import ClientT_Co_D, ClientT_D

from revolt import File, Message, Messageable, MessageReply, SendableEmbed

if TYPE_CHECKING:
    from .cog import Cog

__all__ = ("MessagePayload", "HelpCommand", "DefaultHelpCommand", "help_command_impl")


class MessagePayload(TypedDict):
    content: str
    embed: NotRequired[SendableEmbed]
    embeds: NotRequired[list[SendableEmbed]]
    attachments: NotRequired[list[File]]
    replies: NotRequired[list[MessageReply]]

class HelpCommand(ABC, Generic[ClientT_Co_D]):
    @abstractmethod
    async def create_global_help(self, context: Context[ClientT_Co_D], commands: dict[Optional[Cog[ClientT_Co_D]], list[Command[ClientT_Co_D]]]) -> Union[str, SendableEmbed, MessagePayload]:
        raise NotImplementedError

    @abstractmethod
    async def create_command_help(self, context: Context[ClientT_Co_D], command: Command[ClientT_Co_D]) -> Union[str, SendableEmbed, MessagePayload]:
        raise NotImplementedError

    @abstractmethod
    async def create_group_help(self, context: Context[ClientT_Co_D], group: Group[ClientT_Co_D]) -> Union[str, SendableEmbed, MessagePayload]:
        raise NotImplementedError

    @abstractmethod
    async def create_cog_help(self, context: Context[ClientT_Co_D], cog: Cog[ClientT_Co_D]) -> Union[str, SendableEmbed, MessagePayload]:
        raise NotImplementedError

    async def send_help_command(self, context: Context[ClientT_Co_D], message_payload: MessagePayload) -> Message:
        return await context.send(**message_payload)

    async def filter_commands(self, context: Context[ClientT_Co_D], commands: list[Command[ClientT_Co_D]]) -> list[Command[ClientT_Co_D]]:
        filtered: list[Command[ClientT_Co_D]] = []

        for command in commands:
            if command.hidden:
                continue

            try:
                if await context.can_run(command):
                    filtered.append(command)
            except Exception:
                pass

        return filtered

    async def group_commands(self, context: Context[ClientT_Co_D], commands: list[Command[ClientT_Co_D]]) -> dict[Optional[Cog[ClientT_Co_D]], list[Command[ClientT_Co_D]]]:
        cogs: dict[Optional[Cog[ClientT_Co_D]], list[Command[ClientT_Co_D]]] = {}

        for command in commands:
            cogs.setdefault(command.cog, []).append(command)

        return cogs

    async def handle_message(self, context: Context[ClientT_Co_D], message: Message) -> None:
        pass

    async def get_channel(self, context: Context) -> Messageable:
        return context

    @abstractmethod
    async def handle_no_command_found(self, context: Context[ClientT_Co_D], name: str) -> Union[str, SendableEmbed, MessagePayload]:
        raise NotImplementedError

class DefaultHelpCommand(HelpCommand[ClientT_Co_D]):
    def __init__(self, default_cog_name: str = "No Cog"):
        self.default_cog_name = default_cog_name

    async def create_global_help(self, context: Context[ClientT_Co_D], commands: dict[Optional[Cog[ClientT_Co_D]], list[Command[ClientT_Co_D]]]) -> Union[str, SendableEmbed, MessagePayload]:
        lines = ["```"]

        for cog, cog_commands in commands.items():
            cog_lines: list[str] = []
            cog_lines.append(f"{cog.qualified_name if cog else self.default_cog_name}:")

            for command in cog_commands:
                cog_lines.append(f"  {command.name} - {command.short_description or 'No description'}")

            lines.append("\n".join(cog_lines))

        lines.append("```")
        return "\n".join(lines)

    async def create_cog_help(self, context: Context[ClientT_Co_D], cog: Cog[ClientT_Co_D]) -> Union[str, SendableEmbed, MessagePayload]:
        lines = ["```"]

        lines.append(f"{cog.qualified_name}:")

        for command in cog.commands:
            lines.append(f"  {command.name} - {command.short_description or 'No description'}")

        lines.append("```")
        return "\n".join(lines)

    async def create_command_help(self, context: Context[ClientT_Co_D], command: Command[ClientT_Co_D]) -> Union[str, SendableEmbed, MessagePayload]:
        lines = ["```"]

        lines.append(f"{command.name}:")
        lines.append(f"  Usage: {command.get_usage()}")

        if command.aliases:
            lines.append(f"  Aliases: {', '.join(command.aliases)}")


        if command.description:
            lines.append(command.description)

        lines.append("```")
        return "\n".join(lines)

    async def create_group_help(self, context: Context[ClientT_Co_D], group: Group[ClientT_Co_D]) -> Union[str, SendableEmbed, MessagePayload]:
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

    async def handle_no_command_found(self, context: Context[ClientT_Co_D], name: str) -> str:
        return f"Command `{name}` not found."

class HelpCommandImpl(Command[ClientT_Co_D]):
    def __init__(self, client: ClientT_Co_D):
        self.client = client

        async def callback(_: Union[ClientT_Co_D, Cog[ClientT_Co_D]], context: Context[ClientT_Co_D], *args: str) -> None:
            await help_command_impl(context.client, context, *args)

        super().__init__(callback=callback, name="help", aliases=[])
        self.description: str | None = "Shows help for a command, cog or the entire bot"


async def help_command_impl(client: ClientT_D, context: Context[ClientT_D], *arguments: str) -> None:
    help_command = client.help_command

    if not help_command:
        return

    filtered_commands = await help_command.filter_commands(context, client.commands)
    commands = await help_command.group_commands(context, filtered_commands)

    if not arguments:
        payload = await help_command.create_global_help(context, commands)

    else:
        parent: ClientT_D | Group[ClientT_D] = client

        for param in arguments:
            try:
                command = parent.get_command(param)
            except LookupError:
                try:
                    cog = client.get_cog(param)
                except LookupError:
                    payload = await help_command.handle_no_command_found(context, param)
                else:
                    payload = await help_command.create_cog_help(context, cog)
                finally:
                    break

            if isinstance(command, Group):
                command = cast(Group[ClientT_D], command)
                parent = command
            else:
                payload = await help_command.create_command_help(context, command)
                break
        else:

            if TYPE_CHECKING:
                command = cast(Command[ClientT_D], ...)

            if isinstance(command, Group):
                payload = await help_command.create_group_help(context, command)
            else:
                payload = await help_command.create_command_help(context, command)

    if TYPE_CHECKING:
        payload = cast(MessagePayload, ...)

    msg_payload: MessagePayload

    if isinstance(payload, str):
        msg_payload = {"content": payload}
    elif isinstance(payload, SendableEmbed):
        msg_payload = {"embed": payload, "content": " "}
    else:
        msg_payload = payload

    message = await help_command.send_help_command(context, msg_payload)
    await help_command.handle_message(context, message)
