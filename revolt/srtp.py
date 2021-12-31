import time
import random
import bitarray

class SecureRTP:
    def __init__(self, salt: str, hash: str):
        self.salt = salt
        self.hash = hash
        self.roc = 0
        self.seq = 0
        self.packet_counter = 0
        self.ssrc = random.randbytes(4)  # 32 bytes
        self.version = [1, 0]  # binary for 2

    # documentation of header can be found at https://datatracker.ietf.org/doc/html/rfc3550#section-5.1

    def create_packet(self, data: bytes) -> bytes:
        arr = bitarray.bitarray()

        arr.extend(self.version)
        arr.extend([0, 0])
        arr.extend([0, 0, 0, 0])
        arr.append(0)
        arr.extend([0, 0, 0, 0, 0, 0, 0])

        seq = list(map(int, bin(self.seq)[2:]))
        arr.extend(([0] * (16 - len(seq))) + seq)

        timestamp = list(map(int, bin(int(time.monotonic()))[2:]))

        arr.extend(([0] * (32 - len(timestamp))) + timestamp)
        arr.extend(self.ssrc)

        arr.extend(data)

        return arr.tobytes()
