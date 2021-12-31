from typing import Optional, TypedDict, Union, Literal
from typing_extensions import NotRequired

TransportProtocol = Literal["TCP", "UDP"]

class BaseWS(TypedDict):
    id: NotRequired[int]

class AuthenticationCommandData(TypedDict):
    token: str
    roomId: str

class AuthenticateCommand(BaseWS):
    type: Literal["Authenticate"]

    data: AuthenticationCommandData

class RTPCodecFeedback(TypedDict):
    parameter: str
    type: str

class RTPCodec(TypedDict):
    channels: int
    clockRate: int
    kind: str
    mimeType: str
    parameters: dict
    preferredPayloadType: int
    rtcpFeedback: list[RTPCodecFeedback]

class RTPHeaderExtension(TypedDict):
    direction: str
    kind: str
    preferredEncrypt: bool
    preferredId: int
    uri: str

class RTPCapabilities(TypedDict):
    codecs: list[RTPCodec]
    headerExtensions: list[RTPHeaderExtension]

class AuthenticationResponseData(TypedDict):
    roomId: str
    userId: str
    version: str
    rtpCapabilities: RTPCapabilities

class AuthenticateResponse(BaseWS):
    type: Literal["Authenticate"]
    data: AuthenticationResponseData

class RoomInfoCommand(BaseWS):
    type: Literal["RoomInfo"]

class VoiceUser(TypedDict):
    audio: bool

class RoomInfoResponseData(TypedDict):
    id: str
    users: dict[str, VoiceUser]
    videoAllowed: bool

class RoomInfoResponse(BaseWS):
    type: Literal["RoomInfo"]
    data: RoomInfoResponseData

class InitializeTransportCommandData(TypedDict):
    mode: Literal["SplitWebRTC", "CombinedWebRTC", "CombinedRTP"]
    rtpCapabilities: RTPCapabilities

class InitializeTransportCommand(BaseWS):
    type: Literal["InitializeTransports"]
    data: InitializeTransportCommandData

class IceParameters(TypedDict):
    usernameFragment: str
    password: str
    iceLite: NotRequired[bool]

class IceCandidate(TypedDict):
    foundation: str
    priority: str
    ip: str
    protocol: TransportProtocol
    tcp_type: NotRequired[Literal["passive"]]

class DTLSFingerprints(TypedDict):
    algorithm: Literal["Sha1", "Sha224", "Sha256", "Sha384", "Sha512"]
    value: str

class DtlsParameters(TypedDict):
    role: Literal["auto", "client", "server"]
    fingerprints: list[DTLSFingerprints]

class SctpParameters(TypedDict):
    port: int
    OS: int
    MIS: int
    max_message_size: int

class TransportInfo(TypedDict):
    id: str
    iceParameters: IceParameters
    iceCandidates: list[IceCandidate]
    dtlsParameters: DtlsParameters
    sctpParameters: Optional[SctpParameters]

class InitializeTransportResponseDataSplitWebRTC(TypedDict):
    recvTransport: TransportInfo
    sendTransport: TransportInfo

class InitializeTransportResponseDataCombinedWebRTC(TypedDict):
    transport: TransportInfo

class InitializeTransportResponseDataCombinedRtp(TypedDict):
    ip: bytes
    port: int
    protocol: TransportProtocol
    id: str
    srtpCryptoSuite: Literal["AES_CM_128_HMAC_SHA1_80", "AES_CM_128_HMAC_SHA1_32"]

InitializeTransportResponseData = Union[InitializeTransportResponseDataSplitWebRTC, InitializeTransportResponseDataCombinedWebRTC, InitializeTransportResponseDataCombinedRtp]

class InitializeTransportResponse(BaseWS):
    type: Literal["InitializeTransports"]
    data: InitializeTransportResponseData

class SrtpParameters(TypedDict):
    cryptoSuite: Literal["AES_CM_128_HMAC_SHA1_80", "AES_CM_128_HMAC_SHA1_32"]
    keyBase64: str

class ConnectTransportData(TypedDict):
    id: str
    dtlsParameters: NotRequired[DtlsParameters]
    srtpParameters: NotRequired[SrtpParameters]

class ConnectTransportCommand(BaseWS):
    type: Literal["ConnectTransport"]
    data: ConnectTransportData

class ConnectTransportResponse(BaseWS):
    type: Literal["ConnectTransport"]

class RTPEncodingRtx(TypedDict):
    ssrc: int

class RTPEncoding(TypedDict, total=False):
    ssrc: int
    rid: str
    codec_payload_type: int
    rtx: RTPEncodingRtx
    dtx: bool
    scalability_mode: str
    scale_resolution_down_by: float
    max_bitrate: int

class RTPHeaderExtensionParameters(TypedDict):
    uri: str
    id: int
    encrypt: bool

class RtcpParameters(TypedDict):
    cname: NotRequired[str]
    reduceSize: bool
    mux: NotRequired[bool]

class RTPParameters(TypedDict):
    mid: NotRequired[str]
    codecs: list[RTPCodec]
    headerExtensions: list[RTPHeaderExtensionParameters]
    encodings: list[RTPEncoding]
    rtcp: RtcpParameters

class StartProduceCommandData(TypedDict):
    type: Literal["audio", "video", "saudio", "svideo"]
    rtpParameters: RTPParameters

class StartProduceCommand(BaseWS):
    type: Literal["StartProduce"]
    data: StartProduceCommandData

class StartProduceResponseData(TypedDict):
    producerId: str

class StartProduceResponse(BaseWS):
    type: Literal["StartProduce"]
    data: StartProduceResponseData

WSCommand = Union[AuthenticateCommand, RoomInfoCommand, InitializeTransportCommand, ConnectTransportCommand, StartProduceCommand]
WSResponse = Union[AuthenticateResponse, RoomInfoResponse, InitializeTransportResponse, ConnectTransportResponse, StartProduceResponse]

__all__ = ("BaseWS", "WSCommand", "WSResponse", "AuthenticateCommand", "RoomInfoCommand", "InitializeTransportCommand", "ConnectTransportCommand", "StartProduceCommand", "AuthenticateResponse", "RoomInfoResponse", "InitializeTransportResponse", "ConnectTransportResponse", "StartProduceResponse")
