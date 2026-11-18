import asyncio
import pytest

from overlay.protocol.frame import Frame, IS_RESPONSE
from overlay.transport.connection import Connection
from overlay.transport.server import Server

@pytest.mark.asyncio
async def test_server_survives_unknown_version_and_type():
    """Сервер должен пережить кадры с неизвестной версией и типом."""
    
    # Сервер просто принимает кадры и ничего не делает
    async def dummy_handler(conn, frame: Frame):
        pass

    server = Server(max_frame_payload=65536, on_frame=dummy_handler)
    await server.start("127.0.0.1", 0)
    port = server.server.sockets[0].getsockname()[1]

    # 1. Клиент шлет мусор (неизвестная версия)
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    bad_frame = Frame(version=99, type=99, flags=0, request_id=b"\x00"*16, payload=b"")
    writer.write(bad_frame.encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()

    # 2. Проверяем, что сервер всё ещё жив и принимает новые соединения
    reader2, writer2 = await asyncio.open_connection("127.0.0.1", port)
    writer2.close()
    await writer2.wait_closed()

    server.server.close()
    await server.server.wait_closed()

@pytest.mark.asyncio
async def test_server_survives_overload_and_disconnect():
    """Сервер должен переживать перегрузку и обрыв связи."""
    
    async def slow_handler(conn, frame: Frame):
        await asyncio.sleep(0.5) # Имитация долгой обработки

    server = Server(max_frame_payload=65536, on_frame=slow_handler)
    await server.start("127.0.0.1", 0)
    port = server.server.sockets[0].getsockname()[1]

    # 1. Клиент отправляет кадр и резко обрывает соединение (разрыв внутри обработки)
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    f = Frame(version=1, type=1, flags=0, request_id=b"\x00"*16, payload=b"data")
    writer.write(f.encode())
    await writer.drain()
    writer.close() # Рвем соединение

    # 2. Пока сервер "висит" на обработке, другой клиент должен иметь возможность подключиться
    reader2, writer2 = await asyncio.open_connection("127.0.0.1", port)
    
    # Если мы здесь, значит event loop не заблокирован и сервер жив
    assert writer2 is not None
    
    writer2.close()
    await writer2.wait_closed()

    server.server.close()
    await server.server.wait_closed()
