from __future__ import annotations

import json
import logging
import asyncio
import aiohttp
import random
import string
import nacl
import nacl.public
import nacl.encoding
import nacl.utils
import base64

from typing import TYPE_CHECKING, Literal, BinaryIO

from revolt.types.voice import AuthenticationResponseData, InitializeTransportResponseDataCombinedRtp, RTPCapabilities, RTPHeaderExtensionParameters, StartProduceResponseData

if TYPE_CHECKING:
    from .state import State
    from .types.voice import *

__all__ = ("VoiceClient",)

logger = logging.getLogger("revolt.voice_client")

class VoiceClient:
    __slots__ = ("session", "token", "websocket", "dispatch", "state", "ws_url", "channel_id", "loop", "id", "futures", "capabilities", "rtp_info", "ssrc", "cname", "producer_id", "key", "salt")

    def __init__(self, session: aiohttp.ClientSession, ws_url: str, channel_id: str, token: str, state: State):
        self.id = 0
        self.session = session
        self.ws_url = ws_url
        self.channel_id = channel_id
        self.websocket: aiohttp.ClientWebSocketResponse
        self.token = token
        self.dispatch = state.dispatch
        self.state = state
        self.loop = asyncio.get_running_loop()
        self.futures = dict[int, asyncio.Future]()
        self.ssrc = random.randint(0, 1 << 31)
        self.cname = "".join(random.choices(string.ascii_letters, k=15))

        self.capabilities: RTPCapabilities
        self.rtp_info: InitializeTransportResponseDataCombinedRtp
        self.producer_id: str
        self.key = nacl.utils.random(16)
        self.salt = nacl.utils.random(14)

    async def send_payload(self, payload) -> int:
        self.id += 1
        payload["id"] = self.id

        logging.info(payload)

        await self.websocket.send_str(json.dumps(payload))

        return self.id

    async def heartbeat(self):
        while not self.websocket.closed:
            # logger.info("Sending voice hearbeat")
            await self.websocket.ping()
            await asyncio.sleep(15)

    async def send_authenticate(self):
        payload: AuthenticateCommand = {
            "type": "Authenticate",
            "data": {
                "token": self.token,
                "roomId": self.channel_id
            }
        }

        id = await self.send_payload(payload)
        response: AuthenticationResponseData = await self.set_future(id)
        self.capabilities = response["rtpCapabilities"]

    async def send_initialize_transport(self):
        payload: InitializeTransportCommand = {
            "type": "InitializeTransports",
            "data": {
                "mode": "CombinedRTP",
                "rtpCapabilities": self.capabilities
            }
        }

        id = await self.send_payload(payload)
        response: InitializeTransportResponseDataCombinedRtp = await self.set_future(id)
        self.rtp_info = response

    async def send_connect_transport(self):
        payload: ConnectTransportCommand = {
            "type": "ConnectTransport",
            "data": {
                "srtpParameters": {
                    "cryptoSuite": self.rtp_info["srtpCryptoSuite"],
                    "keyBase64": base64.b64encode(self.salt + self.key).decode(),
                },
                "id": self.rtp_info["id"],
            }
        }

        await self.send_payload(payload)

    async def send_start_produce(self, type: Literal["audio", "video", "saudio", "svideo"]):
        header_extensions: list[RTPHeaderExtensionParameters] = [{"uri": d["uri"], "id": d["preferredId"], "encrypt": d["preferredEncrypt"]} for d in self.capabilities["headerExtensions"]]
        payload: StartProduceCommand = {
            "type": "StartProduce",
            "data": {
                "type": type,
                "rtpParameters": {
                    "codecs": self.capabilities["codecs"],
                    "headerExtensions": header_extensions,
                    "encodings": [{
                        "ssrc": self.ssrc,
                    }],
                    "mid": "0",
                    "rtcp": {
                        "cname": self.cname,
                        "reduceSize": True
                    }
                }
            }
        }

        id = await self.send_payload(payload)
        response: StartProduceResponseData = await self.set_future(id)
        producer_id = response["producerId"]
        self.producer_id = producer_id

    async def handle_event(self, payload: WSResponse):
        event_type = payload["type"].lower()
        logger.debug("Recieved event %s %s", event_type, payload)

        try:
            func = getattr(self, f"handle_{event_type}")
        except:
            logger.debug("Unknown event '%s'", event_type)
            return

        await func(payload)

    async def handle_authenticate(self, _):
        logger.info("Successfully authenticated")

    async def set_future(self, id: int):
        future = asyncio.Future()
        self.futures[id] = future
        return await future

    async def websocket_loop(self):
        async for msg in self.websocket:
            payload: WSResponse = json.loads(msg.data)
            print(payload)

            if future := self.futures.get(payload.get("id", "")):
                future.set_result(payload.get("data"))

            self.loop.create_task(self.handle_event(payload))

    async def start(self):
        self.websocket = await self.session.ws_connect(self.ws_url)

        asyncio.create_task(self.heartbeat())
        asyncio.create_task(self.websocket_loop())

    async def send_audio(self, audio: BinaryIO):
        await self.send_start_produce("audio")


"""
{
    'type': 'StartProduce',
    'data': {
        'type': 'audio',
        'rtpParameters': {
            'codecs': [
                {'kind': 'audio', 'mimeType': 'audio/opus', 'preferredPayloadType': 100, 'clockRate': 48000, 'channels': 2, 'parameters': {}, 'rtcpFeedback': [{'type': 'transport-cc', 'parameter': ''}]}
            ],
            'headerExtensions': [{'uri': 'urn:ietf:params:rtp-hdrext:sdes:mid', 'id': 1, 'encrypt': False}, {'uri': 'urn:ietf:params:rtp-hdrext:sdes:mid', 'id': 1, 'encrypt': False}, {'uri': 'urn:ietf:params:rtp-hdrext:sdes:rtp-stream-id', 'id': 2, 'encrypt': False}, {'uri': 'urn:ietf:params:rtp-hdrext:sdes:repaired-rtp-stream-id', 'id': 3, 'encrypt': False}, {'uri': 'http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time', 'id': 4, 'encrypt': False}, {'uri': 'http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time', 'id': 4, 'encrypt': False}, {'uri': 'http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01', 'id': 5, 'encrypt': False}, {'uri': 'http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01', 'id': 5, 'encrypt': False}, {'uri': 'http://tools.ietf.org/html/draft-ietf-avtext-framemarking-07', 'id': 6, 'encrypt': False}, {'uri': 'urn:ietf:params:rtp-hdrext:framemarking', 'id': 7, 'encrypt': False}, {'uri': 'urn:ietf:params:rtp-hdrext:ssrc-audio-level', 'id': 10, 'encrypt': False}, {'uri': 'urn:3gpp:video-orientation', 'id': 11, 'encrypt': False}, {'uri': 'urn:ietf:params:rtp-hdrext:toffset', 'id': 12, 'encrypt': False}],
            'encodings': [{'ssrc': 896646738}],
            'mid': '0',
            'rtcp': {'cname': 'iUaoUqyQjShruzl', 'reduceSize': True}}
    },
    'id': 4}
"""
"""
{
    "type": "StartProduce",
    "data": {
        "type":"audio",
        "rtpParameters": {
            "codecs": [
                {"mimeType":"audio/opus","payloadType":111,"clockRate":48000,"channels":2,"parameters":{"minptime":10,"useinbandfec":1},"rtcpFeedback":[{"type":"transport-cc","parameter":""}]}
            ],
            "headerExtensions":[{"uri":"urn:ietf:params:rtp-hdrext:sdes:mid","id":4,"encrypt":false,"parameters":{}},{"uri":"http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time","id":2,"encrypt":false,"parameters":{}},{"uri":"http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01","id":3,"encrypt":false,"parameters":{}},{"uri":"urn:ietf:params:rtp-hdrext:ssrc-audio-level","id":1,"encrypt":false,"parameters":{}}],
            "encodings":[{"ssrc":2276570677,"dtx":false}],
            "mid":"0"}
        "rtcp":{"cname":"KAhFB58ELM5Tf+9a","reducedSize":true},
        }
    }
    "id":7,
"""
