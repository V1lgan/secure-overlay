from __future__ import annotations

import struct
from dataclasses import dataclass

HEADER_FORMAT = "!BBH16sI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # == 24
assert HEADER_SIZE == 24

# Флаги
IS_RESPONSE = 0x0001
IS_ERROR = 0x0002
IS_FRAGMENT = 0x0004


@dataclass(frozen=True)
class Frame:
    version: int
    type: int
    flags: int
    request_id: bytes
    payload: bytes

    def encode(self) -> bytes:
        if len(self.request_id) != 16:
            raise ValueError("request_id must be 16 bytes")
        if not (0 <= self.type <= 0xFF):
            raise ValueError("type out of uint8 range")
        if not (0 <= self.version <= 0xFF):
            raise ValueError("version out of uint8 range")
        if not (0 <= self.flags <= 0xFFFF):
            raise ValueError("flags out of uint16 range")
        header = struct.pack(
            HEADER_FORMAT,
            self.version,
            self.type,
            self.flags,
            self.request_id,
            len(self.payload),
        )
        return header + self.payload


@dataclass(frozen=True)
class Header:
    version: int
    type: int
    flags: int
    request_id: bytes
    payload_length: int


def decode_header(buf: bytes) -> Header:
    if len(buf) != HEADER_SIZE:
        raise ValueError("header must be exactly 24 bytes")
    version, type_, flags, request_id, payload_length = struct.unpack(
        HEADER_FORMAT, buf
    )
    return Header(version, type_, flags, request_id, payload_length)
