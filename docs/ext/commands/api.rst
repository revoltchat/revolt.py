.. currentmodule:: revolt

API Reference
===============


CommandsClient
~~~~~~~~~~~~~~~
.. autoclass:: revolt.ext.commands.CommandsClient
    :members:

Context
~~~~~~~~
.. autoclass:: revolt.ext.commands.Context
    :members:

Command
~~~~~~~~
.. autoclass:: revolt.ext.commands.Command
    :members:

Group
~~~~~~~~
.. autoclass:: revolt.ext.commands.Group
    :members:

Cog
~~~~
.. autoclass:: revolt.ext.commands.Cog
    :members:

command
~~~~~~~~
.. autodecorator:: revolt.ext.commands.command

group
~~~~~~~~
.. autodecorator:: revolt.ext.commands.group

Checks
-------

check
~~~~~~
.. autodecorator:: revolt.ext.commands.check

is_bot_owner
~~~~~~~~~~~~~
.. autodecorator:: revolt.ext.commands.is_bot_owner

is_server_owner
~~~~~~~~~~~~~~~~
.. autodecorator:: revolt.ext.commands.is_server_owner

has_permissions
~~~~~~~~~~~~~~~~
.. autodecorator:: revolt.ext.commands.has_permissions

has_channel_permissions
~~~~~~~~~~~~~~~~~~~~~~~~
.. autodecorator:: revolt.ext.commands.has_channel_permissions

Converters
-----------

IntConverter
~~~~~~~~~~~~~
Converts the parameter to an int

BoolConverter
~~~~~~~~~~~~~~
Converts the parameter to a bool

CategoryConverter
~~~~~~~~~~~~~~~~~~
Converts the parameter to a category

UserConverter
~~~~~~~~~~~~~~
Converts the parameter to a category

MemberConverter
~~~~~~~~~~~~~~~~
Converts the parameter to a category

ChannelConverter
~~~~~~~~~~~~~~~~~
Converts the parameter to a category

Greedy
~~~~~~
Converts the parameter to a greedy parameter which will take as many arguments which convert successfully.

Allows you to have var-args in the middle of a signature.

Help Commands
--------------

HelpCommand
~~~~~~~~~~~~
.. autoclass:: revolt.ext.commands.HelpCommand
    :members:

DefaultHelpCommand
~~~~~~~~~~~~~~~~~~~
.. autoclass:: revolt.ext.commands.DefaultHelpCommand
    :members:

Exceptions
-----------

CommandError
~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.CommandError
    :members:

CommandNotFound
~~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.CommandNotFound
    :members:

NoClosingQuote
~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.NoClosingQuote
    :members:

CheckError
~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.CheckError
    :members:

NotBotOwner
~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.NotBotOwner
    :members:

NotServerOwner
~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.NotServerOwner
    :members:

ServerOnly
~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.ServerOnly
    :members:

MissingPermissionsError
~~~~~~~~~~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.MissingPermissionsError
    :members:

ConverterError
~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.ConverterError
    :members:

InvalidLiteralArgument
~~~~~~~~~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.InvalidLiteralArgument
    :members:

BadBoolArgument
~~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.BadBoolArgument
    :members:

CategoryConverterError
~~~~~~~~~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.CategoryConverterError
    :members:

ChannelConverterError
~~~~~~~~~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.ChannelConverterError
    :members:

UserConverterError
~~~~~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.UserConverterError
    :members:

MemberConverterError
~~~~~~~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.MemberConverterError
    :members:

UnionConverterError
~~~~~~~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.UnionConverterError
    :members:

MissingSetup
~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.MissingSetup
    :members:

CommandOnCooldown
~~~~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.CommandOnCooldown
    :members: