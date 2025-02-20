from __future__ import annotations

import sys
import traceback
from importlib import import_module
from typing import (TYPE_CHECKING, Any, Coroutine, Optional, Protocol, TypeVar, Union,
                    overload, runtime_checkable)

from typing_extensions import Self

import revolt

if TYPE_CHECKING:
    from .help import HelpCommand

    import aiohttp

from .cog import Cog
from .command import Command
from .context import Context
from .errors import CheckError, CommandNotFound, MissingSetup
from .view import StringView

__all__ = (
    "CommandsMeta",
    "CommandsClient"
)

V = TypeVar("V")
T = TypeVar("T")

@runtime_checkable
class ExtensionProtocol(Protocol):
    @staticmethod
    def setup(client: CommandsClient) -> None:
        raise NotImplementedError

class CommandsMeta(type):
    _commands: list[Command[Any]]

    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> Any:
        commands: list[Command[Any]] = []
        self = super().__new__(cls, name, bases, attrs)

        for base in reversed(self.__mro__):
            for value in base.__dict__.values():
                if isinstance(value, Command) and value.parent is None:  # type: ignore
                    commands.append(value)  # type: ignore

        self._commands = commands

        return self


class CaseInsensitiveDict(dict[str, V]):
    def __setitem__(self, key: str, value: V) -> None:
        super().__setitem__(key.casefold(), value)

    def __getitem__(self, key: str) -> V:
        return super().__getitem__(key.casefold())

    def __contains__(self, key: object) -> bool:
        if isinstance(key, str):
            return super().__contains__(key.casefold())
        else:
            return False

    @overload
    def get(self, key: str) -> V | None:
        ...

    @overload
    def get(self, key: str, default: V | T) -> V | T:
        ...

    def get(self, key: str, default: Optional[T] = None) -> V | T | None:
        return super().get(key.casefold(), default)

    def __delitem__(self, key: str) -> None:
        super().__delitem__(key.casefold())


class CommandsClient(revolt.Client, metaclass=CommandsMeta):
    """A subclass of :class:`~revolt.Client` which has support for commands.

    Parameters
    -----------
    session: :class:`~aiohttp.ClientSession`
        The aiohttp session to use for http request and the websocket
    token: :class:`str`
        The bots token
    api_url: :class:`str`
        The api url for the revolt instance you are connecting to, by default it uses the offical instance hosted at revolt.chat
    max_messages: :class:`int`
        The max amount of messages stored in the cache, by default this is 5k
    bot: :class:`bool`
        Denotes whether the account used is a bot account or user account, by default this it assumes a bot account
    help_command: Optional[:class:`~revolt.ext.commands.HelpCommand`]
        Sets the custom help command, or remove it if passed ``None``
    case_insensitive: :class:`bool`
        Whether or not commands should be case insensitive
    """

    _commands: list[Command[Self]]

    def __init__(
        self,
        session: aiohttp.ClientSession,
        token: str,
        *,
        api_url: str = "https://api.revolt.chat",
        max_messages: int = 5000,
        bot: bool = True,
        help_command: Union[HelpCommand[Self], None, revolt.utils._Missing] = revolt.utils.Missing,
        case_insensitive: bool = False
    ):
        from .help import DefaultHelpCommand, HelpCommandImpl

        self.all_commands: dict[str, Command[Self]] | CaseInsensitiveDict[Command[Self]] = {} if not case_insensitive else CaseInsensitiveDict()
        self.cogs: dict[str, Cog[Self]] = {}
        self.extensions: dict[str, ExtensionProtocol] = {}

        for command in self._commands:
            self.all_commands[command.name] = command

            for alias in command.aliases:
                self.all_commands[alias] = command

        self.help_command: HelpCommand[Self] | None

        if help_command is not None:
            self.help_command = help_command or DefaultHelpCommand[Self]()
            self.add_command(HelpCommandImpl(self))
        else:
            self.help_command = None

        super().__init__(session, token, api_url=api_url, max_messages=max_messages, bot=bot)

    @property
    def commands(self) -> list[Command[Self]]:
        """Gets all commands registered

        Returns
        --------
        list[:class:`Command`]
            The registered commands
        """
        return list(set(self.all_commands.values()))

    async def get_prefix(self, message: revolt.Message) -> Union[str, list[str]]:
        """Overwrite this function to set the prefix used for commands, this function is called for every message.

        Parameters
        -----------
        message: :class:`Message`
            The message that was sent

        Returns
        --------
        Union[:class:`str`, list[:class:`str`]]
            The prefix(s) for the commands
        """
        raise NotImplementedError

    def get_command(self, name: str) -> Command[Self]:
        """Gets a command.

        Parameters
        -----------
        name: :class:`str`
            The name or alias of the command

        Returns
        --------
        :class:`Command`
            The command with the name
        """
        return self.all_commands[name]

    def add_command(self, command: Command[Self]) -> None:
        """Adds a command, this is typically only used for dynamic commands, you should use the `commands.command` decorator for most usecases.

        Parameters
        -----------
        name: :class:`str`
            The name or alias of the command
        command: :class:`Command`
            The command to be added
        """
        self.all_commands[command.name] = command

        for alias in command.aliases:
            self.all_commands[alias] = command

    def remove_command(self, name: str) -> Optional[Command[Self]]:
        """Removes a command.

        Parameters
        -----------
        name: :class:`str`
            The name or alias of the command

        Returns
        --------
        Optional[:class:`Command`]
            The command that was removed
        """
        command = self.all_commands.pop(name, None)

        if command is not None:
            for alias in command.aliases:
                self.all_commands.pop(alias, None)

        return command

    def get_view(self, message: revolt.Message) -> type[StringView]:
        """Returns the StringView class to use, this can be overwritten to customize how arguments are parsed

        Returns
        --------
        type[:class:`StringView`]
            The string view class to use
        """
        return StringView

    def get_context(self, message: revolt.Message) -> type[Context[Self]]:
        """Returns the Context class to use, this can be overwritten to add extra features to context

        Returns
        --------
        type[:class:`Context`]
            The context class to use
        """
        return Context[Self]

    async def process_commands(self, message: revolt.Message) -> Any:
        """Processes commands, if you overwrite `Client.on_message` you should manually call this function inside the event.

        Parameters
        -----------
        message: :class:`Message`
            The message to process commands on

        Returns
        --------
        Any
            The return of the command, if any
        """
        content = message.content

        prefixes = await self.get_prefix(message)

        if isinstance(prefixes, str):
            prefixes = [prefixes]

        for prefix in prefixes:
            if content.startswith(prefix):
                content = content[len(prefix):]
                break
        else:
            return

        if not content:
            return

        view = self.get_view(message)(content)

        try:
            command_name = view.get_next_word()
        except StopIteration:
            return

        context_cls = self.get_context(message)

        try:
            command = self.get_command(command_name)
        except KeyError:
            context = context_cls(None, command_name, view, message, self)
            return self.dispatch("command_error", context, CommandNotFound(command_name))

        context = context_cls(command, command_name, view, message, self)

        try:
            self.dispatch("command", context)

            if not await self.global_check(context):
                raise CheckError(f"the global check for the command failed")

            if not await context.can_run():
                raise CheckError(f"the check(s) for the command failed")

            output = await context.invoke()
            self.dispatch("after_command_invoke", context, output)

            return output
        except Exception as e:
            await command._error_handler(command.cog or self, context, e)
            self.dispatch("command_error", context, e)

    async def on_command_error(self, ctx: Context[Self], error: Exception, /) -> None:
        traceback.print_exception(type(error), error, error.__traceback__)

    def on_message(self, message: revolt.Message) -> Coroutine[Any, Any, Any]:
        return self.process_commands(message)

    async def global_check(self, context: Context[Self]) -> bool:
        """A global check that stops commands from running on certain criteria.

        Parameters
        -----------
        context: :class:`Context`
            The context for the invokation of the command

        Returns
        --------
        :class:`bool` represents if the command should run or not
        """

        return True

    def add_cog(self, cog: Cog[Self]) -> None:
        """Adds a cog, this cog must subclass `Cog`.

        Parameters
        -----------
        cog: :class:`Cog`
            The cog to be added
        """
        cog._inject(self)

    def remove_cog(self, cog_name: str) -> Cog[Self]:
        """Removes a cog.

        Parameters
        -----------
        cog_name: :class:`str`
            The name of the cog to be removed

        Returns
        --------
        :class:`Cog`
            The cog that was removed
        """
        cog = self.cogs.pop(cog_name)
        cog._uninject(self)

        return cog

    def load_extension(self, name: str) -> None:
        """Loads an extension, this takes a module name and runs the setup function inside of it.

        Parameters
        -----------
        name: :class:`str`
            The name of the extension to be loaded
        """
        extension = import_module(name)

        if not isinstance(extension, ExtensionProtocol):
            raise MissingSetup(f"'{extension}' is missing a setup function")

        self.extensions[name] = extension
        extension.setup(self)

    def unload_extension(self, name: str) -> None:
        """Unloads an extension, this takes a module name and runs the teardown function inside of it.

        Parameters
        -----------
        name: :class:`str`
            The name of the extension to be unloaded
        """
        extension = self.extensions.pop(name)

        del sys.modules[name]

        if teardown := getattr(extension, "teardown", None):
            teardown(self)

    def reload_extension(self, name: str) -> None:
        """Reloads an extension, this will unload and reload the extension.

        Parameters
        -----------
        name: :class:`str`
            The name of the extension to be reloaded
        """
        self.unload_extension(name)
        self.load_extension(name)

    def get_cog(self, name: str) -> Cog[Self]:
        """Gets a cog.

        Parameters
        -----------
        name: :class:`str`
            The name of the cog to get

        Returns
        --------
        :class:`Cog`
            The cog that was requested
        """
        return self.cogs[name]

    def get_extension(self, name: str) -> ExtensionProtocol:
        """Gets an extension.

        Parameters
        -----------
        name: :class:`str`
            The name of the extension to get

        Returns
        --------
        :class:`ExtensionProtocol`
            The extension that was requested
        """
        return self.extensions[name]
