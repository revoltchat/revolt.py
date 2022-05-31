.. currentmodule:: revolt

API Reference
===============


Client
~~~~~~~

.. autoclass:: Client
    :members:

Asset
~~~~~~

.. autoclass:: Asset
    :members:

PartialAsset
~~~~~~~~~~~~~

.. autoclass:: PartialAsset
    :members:


Channel
~~~~~~~~

.. autoclass:: Channel
    :members:

SavedMessageChannel
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: SavedMessageChannel
    :members:

DMChannel
~~~~~~~~~~

.. autoclass:: DMChannel
    :members:

GroupDMChannel
~~~~~~~~~~~~~~~

.. autoclass:: GroupDMChannel
    :members:

TextChannel
~~~~~~~~~~~~

.. autoclass:: TextChannel
    :members:

VoiceChannel
~~~~~~~~~~~~~

.. autoclass:: VoiceChannel
    :members:


Embed
~~~~~~

.. autoclass:: Embed
    :members:

WebsiteEmbed
~~~~~~~~~~~~~

.. autoclass:: WebsiteEmbed
    :members:

ImageEmbed
~~~~~~~~~~~

.. autoclass:: ImageEmbed
    :members:

TextEmbed
~~~~~~~~~~

.. autoclass:: TextEmbed
    :members:

NoneEmbed
~~~~~~~~~~

.. autoclass:: NoneEmbed
    :members:

SendableEmbed
~~~~~~~~~~~~~~

.. autoclass:: SendableEmbed
    :members:

File
~~~~~

.. autoclass:: File
    :members:

Member
~~~~~~~

.. autoclass:: Member
    :members:

Message
~~~~~~~~

.. autoclass:: Message
    :members:

MessageReply
~~~~~~~~~~~~~
.. autoclass:: MessageReply
    :members:

Masquerade
~~~~~~~~~~~~~
.. autoclass:: Masquerade
    :members:

Messageable
~~~~~~~~~~~~

.. autoclass:: Messageable
    :members:

Permissions
~~~~~~~~~~~~

.. autoclass:: Permissions
    :members:

PermissionsOverwrite
~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: PermissionsOverwrite
    :members:

Role
~~~~~

.. autoclass:: Role
    :members:

Server
~~~~~~~

.. autoclass:: Server
    :members:

ServerBan
~~~~~~~~~~

.. autoclass:: ServerBan
    :members:

Category
~~~~~~~~~

.. autoclass:: Category
    :members:


SystemMessages
~~~~~~~~~~~~~~~

.. autoclass:: SystemMessages
    :members:


User
~~~~~

.. autoclass:: User
    :members:

Relation
~~~~~~~~~

.. autonamedtuple:: Relation


Status
~~~~~~~

.. autonamedtuple:: Status

UserBadges
~~~~~~~~~~~

.. autoclass:: UserBadges
    :members:

UserProfile
~~~~~~~~~~~~

.. autoclass:: UserProfile
    :members:

Invite
~~~~~~~

.. autoclass:: Invite
    :members:

Enums
======

The api uses enums to say what variant of something is,
these represent those enums

All enums subclass `aenum.Enum`.

.. class:: ChannelType

    Specifies the type of channel.

    .. attribute:: saved_message

        A private channel only you can access.
    .. attribute:: direct_message

        A private direct message channel between you and another user
    .. attribute:: group

        A private group channel for messages between a group of users
    .. attribute:: text_channel

        A text channel in a server
    .. attribute:: voice_channel

        A voice only channel

.. class:: PresenceType

    Specifies what a users presence is

    .. attribute:: busy

        The user is busy and wont receive notification
    .. attribute:: idle

        The user is idle
    .. attribute:: invisible

        The user is invisible, you will never receive this, instead they will appear offline
    .. attribute:: online

        The user is online

    .. attribute:: offline

        The user is offline or invisible

.. attribute:: RelationshipType

    Specifies the relationship between two users

    .. attribute:: blocked

        You have blocked them
    .. attribute:: blocked_other

        They have blocked you
    .. attribute:: friend

        You are friends with them
    .. attribute:: incoming_friend_request

        They are sending you a friend request
    .. attribute:: none

        You have no relationship with them
    .. attribute:: outgoing_friend_request

        You are sending them a friend request

    .. attribute:: user

        That user is yourself

.. class:: AssetType

    Specifies the type of asset

    .. attribute:: image

        The asset is an image
    .. attribute:: video

        The asset is a video
    .. attribute:: text

        The asset is a text file
    .. attribute:: audio

        The asset is an audio file
    .. attribute:: file

        The asset is a generic file

.. class:: SortType

    The sort type for a message search

    .. attribute:: latest

        Sort by the latest message
    .. attribute:: oldest

        Sort by the oldest message
    .. attribute:: relevance

        Sort by the relevance of the message

.. class:: EmbedType

    The type of embed

    .. attribute:: website

        The embed is a website
    .. attribute:: image

        The embed is an image
    .. attribute:: text

        The embed is text
    .. attribute:: video

        The embed is a video
    .. attribute:: unknown

        The embed is unknown

Utils
======

.. currentmodule:: revolt.utils

A collection a utility functions and classes to aid in making your bot

.. autofunction:: get

.. autodecorator:: client_session
