from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict, Union

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .file import File

__all__ = ("Embed", "SendableEmbed", "WebsiteEmbed", "ImageEmbed", "TextEmbed", "NoneEmbed", "YoutubeSpecial", "TwitchSpecial", "SpotifySpecial", "SoundcloudSpecial", "BandcampSpecial", "WebsiteSpecial", "JanuaryImage", "JanuaryVideo")

class YoutubeSpecial(TypedDict):
    type: Literal["Youtube"]
    id: str
    timestamp: NotRequired[str]

class TwitchSpecial(TypedDict):
    type: Literal["Twitch"]
    content_type: Literal["Channel", "Video", "Clip"]
    id: str

class SpotifySpecial(TypedDict):
    type: Literal["Spotify"]
    content_type: str
    id: str

class SoundcloudSpecial(TypedDict):
    type: Literal["Soundcloud"]

class BandcampSpecial(TypedDict):
    type: Literal["Bandcamp"]
    content_type: Literal["Album", "Track"]
    id: str

WebsiteSpecial = Union[YoutubeSpecial, TwitchSpecial, SpotifySpecial, SoundcloudSpecial, BandcampSpecial]

class JanuaryImage(TypedDict):
    url: str
    width: int
    height: int
    size: Literal["Large", "Preview"]

class JanuaryVideo(TypedDict):
    url: str
    width: int
    height: int

class WebsiteEmbed(TypedDict):
    type: Literal["Website"]
    url: NotRequired[str]
    special: NotRequired[WebsiteSpecial]
    title: NotRequired[str]
    description: NotRequired[str]
    image: NotRequired[JanuaryImage]
    video: NotRequired[JanuaryVideo]
    site_name: NotRequired[str]
    icon_url: NotRequired[str]
    colour: NotRequired[str]

class ImageEmbed(JanuaryImage):
    type: Literal["Image"]

class TextEmbed(TypedDict):
    type: Literal["Text"]
    icon_url: NotRequired[str]
    url: NotRequired[str]
    title: NotRequired[str]
    description: NotRequired[str]
    media: NotRequired[File]
    colour: NotRequired[str]

class NoneEmbed(TypedDict):
    type: Literal["None"]

Embed = Union[WebsiteEmbed, ImageEmbed, TextEmbed, NoneEmbed]

class SendableEmbed(TypedDict):
    type: Literal["Text"]
    icon_url: NotRequired[str]
    url: NotRequired[str]
    title: NotRequired[str]
    description: NotRequired[str]
    media: NotRequired[str]
    colour: NotRequired[str]

