.. currentmodule:: revolt

API Reference
===============


.. autoclass:: Client
    :members:
    :inherited-members:

.. autoclass:: Asset
    :members:
    :inherited-members:

.. autoclass:: PartialAsset
    :members:
    :inherited-members:

.. autoclass:: Channel
    :members:
    :inherited-members:

.. autoclass:: ServerChannel
    :members:
    :inherited-members:

.. autoclass:: SavedMessageChannel
    :members:
    :inherited-members:

.. autoclass:: DMChannel
    :members:
    :inherited-members:

.. autoclass:: GroupDMChannel
    :members:
    :inherited-members:

.. autoclass:: TextChannel
    :members:
    :inherited-members:

.. autoclass:: VoiceChannel
    :members:
    :inherited-members:

.. autoclass:: Embed
    :members:
    :inherited-members:

.. autoclass:: WebsiteEmbed
    :members:
    :inherited-members:

.. autoclass:: ImageEmbed
    :members:
    :inherited-members:

.. autoclass:: TextEmbed
    :members:
    :inherited-members:

.. autoclass:: NoneEmbed
    :members:
    :inherited-members:

.. autoclass:: SendableEmbed
    :members:
    :inherited-members:

.. autoclass:: File
    :members:
    :inherited-members:

.. autoclass:: Member
    :members:
    :inherited-members:

.. autoclass:: Message
    :members:
    :inherited-members:

.. autoclass:: MessageReply
    :members:
    :inherited-members:

.. autoclass:: Masquerade
    :members:
    :inherited-members:

.. autoclass:: Messageable
    :members:
    :inherited-members:

.. autoclass:: Permissions
    :members:
    :inherited-members:

.. autoclass:: UserPermissions
    :members:
    :inherited-members:

.. autoclass:: PermissionsOverwrite
    :members:
    :inherited-members:

.. autoclass:: Role
    :members:
    :inherited-members:

.. autoclass:: Server
    :members:
    :inherited-members:

.. autoclass:: ServerBan
    :members:
    :inherited-members:

.. autoclass:: Category
    :members:
    :inherited-members:

.. autoclass:: SystemMessages
    :members:
    :inherited-members:

.. autoclass:: User
    :members:
    :inherited-members:

.. autonamedtuple:: Relation

.. autonamedtuple:: Status

.. autoclass:: UserBadges
    :members:

.. autoclass:: UserProfile
    :members:

.. autoclass:: Invite
    :members:

.. autoclass:: Emoji
    :members:

.. autoclass:: MessageInteractions
    :members:

Enums
------

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

.. class:: RelationshipType

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
------

.. currentmodule:: revolt.utils

A collection a utility functions and classes to aid in making your bot

.. autofunction:: get

.. autofunction:: client_session

.. autoclass:: Ulid
    :members:

.. autoclass:: Object
    :members: