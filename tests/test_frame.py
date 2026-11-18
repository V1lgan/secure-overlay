import struct

import pytest

from overlay.protocol.frame import (
    HEADER_FORMAT,
    HEADER_SIZE,
    IS_RESPONSE,
    Frame,
    decode_header,
)


def test_header_size_is_24():
    assert HEADER_SIZE == 24
    assert struct.calcsize(HEADER_FORMAT) == 24


def test_roundtrip_all_fields():
    f = Frame(
        version=1,
        type=0x01,
        flags=IS_RESPONSE,
        request_id=bytes(range(16)),
        payload=b"hello",
    )
    raw = f.encode()
    assert len(raw) == 24 + 5
    h = decode_header(raw[:24])
    assert h.version == 1
    assert h.type == 0x01
    assert h.flags == IS_RESPONSE
    assert h.request_id == bytes(range(16))
    assert h.payload_length == 5
    assert raw[24:] == b"hello"


def test_big_endian_flags_and_length():
    f = Frame(version=1, type=1, flags=0x0102, request_id=b"\x00" * 16, payload=b"x")
    raw = f.encode()
    assert raw[2:4] == b"\x01\x02"
    assert raw[20:24] == b"\x00\x00\x00\x01"


def test_request_id_must_be_16_bytes():
    with pytest.raises(ValueError):
        Frame(version=1, type=1, flags=0, request_id=b"short", payload=b"").encode()


def test_uint8_bounds():
    with pytest.raises(ValueError):
        Frame(version=1, type=256, flags=0, request_id=b"\x00" * 16, payload=b"").encode()
