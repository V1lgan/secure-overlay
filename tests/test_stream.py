import random
import pytest
from overlay.protocol.frame import Frame
from overlay.protocol.stream import FrameBuffer


def test_frame_buffer_random_chunks():
    # Генерируем 100 разных кадров
    original_frames = []
    for i in range(100):
        payload = f"payload_{i}".encode() * random.randint(1, 10)
        f = Frame(
            version=1, 
            type=1, 
            flags=0, 
            request_id=i.to_bytes(16, 'big'), 
            payload=payload
        )
        original_frames.append(f)

    # Склеиваем их в один сплошной поток байтов (как будто они пришли подряд)
    stream_data = b"".join(f.encode() for f in original_frames)
    
    buffer = FrameBuffer(max_frame_payload=65536)
    decoded_frames = []

    # Имитируем случайные куски TCP
    pos = 0
    while pos < len(stream_data):
        chunk_size = random.randint(1, 50)
        chunk = stream_data[pos:pos + chunk_size]
        pos += chunk_size
        
        # Получаем кадры, которые полностью собрались
        decoded_frames.extend(buffer.feed(chunk))

    # Проверяем, что декодер собрал ровно 100 кадров
    assert len(decoded_frames) == 100

    # Проверяем, что они совпадают с оригинальными
    for orig, dec in zip(original_frames, decoded_frames):
        assert orig.request_id == dec.request_id
        assert orig.payload == dec.payload

def test_frame_buffer_empty_payload():
    f = Frame(version=1, type=1, flags=0, request_id=b"\x00"*16, payload=b"")
    buffer = FrameBuffer(max_frame_payload=65536)
    frames = buffer.feed(f.encode())
    assert len(frames) == 1
    assert frames[0].payload == b""

def test_frame_buffer_exceeds_limit():
    # E1-6: превышение лимита должно кидать ошибку ДО чтения payload
    f = Frame(version=1, type=1, flags=0, request_id=b"\x00"*16, payload=b"x"*100)
    buffer = FrameBuffer(max_frame_payload=50)
    
    with pytest.raises(ValueError, match="exceeds max limit"):
        buffer.feed(f.encode())
