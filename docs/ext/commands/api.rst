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

command
~~~~~~~~
.. autodecorator:: revolt.ext.commands.command

check
~~~~~~
.. autodecorator:: revolt.ext.commands.check

is_bot_owner
~~~~~~~~~~~~~
.. autodecorator:: revolt.ext.commands.is_bot_owner

is_server_owner
~~~~~~~~~~~~~~~~
.. autodecorator:: revolt.ext.commands.is_server_owner


Exceptions
===========

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

UserConverterError
~~~~~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.UserConverterError
    :members:

MemberConverterError
~~~~~~~~~~~~~~~~~~~~~
.. autoexception:: revolt.ext.commands.MemberConverterError
    :members:
