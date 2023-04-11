from typing import Literal, TypedDict, Union

from typing_extensions import NotRequired


class EmojiParentServer(TypedDict):
    type: Literal["Server"]
    id: str

class EmojiParentDetached(TypedDict):
    type: Literal["Detached"]

EmojiParent = Union[EmojiParentServer, EmojiParentDetached]

class Emoji(TypedDict):
    _id: str
    parent: EmojiParent
    creator_id: str
    name: str
    animated: NotRequired[bool]
    nsfw: NotRequired[bool]
