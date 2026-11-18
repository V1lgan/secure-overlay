import asyncio
import pytest
import secrets

from overlay.protocol.frame import Frame, IS_RESPONSE
from overlay.transport.connection import Connection
from overlay.transport.rpc import RpcClient, RequestTimeout
from overlay.transport.server import Server

@pytest.mark.asyncio
async def test_rpc_unknown_request_id():
    """Сервер отправляет ответ с чужим request_id. Клиент должен его проигнорировать."""
    
    # 1. Создаем сервер, который на любой запрос шлет ответ с НЕПРАВИЛЬНЫМ request_id
    async def bad_handler(conn, frame: Frame):
        bad_response = Frame(
            version=1,
            type=0x02,
            flags=IS_RESPONSE,
            request_id=secrets.token_bytes(16), # Чужой ID!
            payload=b"BAD_PONG"
        )
        await conn.send_frame(bad_response)

    server = Server(max_frame_payload=65536, on_frame=bad_handler)
    # Запускаем сервер на случайном свободном порту (0)
    await server.start("127.0.0.1", 0)
    port = server.server.sockets[0].getsockname()[1]

    # 2. Подключаем клиента
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    conn = Connection(reader, writer, max_frame_payload=65536)
    rpc = RpcClient(conn)
    conn.on_frame = rpc.handle_frame
    read_task = asyncio.create_task(conn.run())

    try:
        # 3. Отправляем запрос. Так как сервер ответит чужим ID, 
        # клиент должен проигнорировать ответ и выбросить RequestTimeout по тайм-ауту.
        with pytest.raises(RequestTimeout):
            await rpc.call(msg_type=0x01, payload=b"PING", timeout=0.5)
            
    finally:
        read_task.cancel()
        await conn.close()
        server.server.close()
        await server.server.wait_closed()

@pytest.mark.asyncio
async def test_rpc_correct_response():
    """Сервер отвечает правильно. Клиент должен получить ответ."""
    
    async def good_handler(conn, frame: Frame):
        good_response = Frame(
            version=1,
            type=0x02,
            flags=IS_RESPONSE,
            request_id=frame.request_id, # Правильный ID
            payload=b"OK"
        )
        await conn.send_frame(good_response)

    server = Server(max_frame_payload=65536, on_frame=good_handler)
    await server.start("127.0.0.1", 0)
    port = server.server.sockets[0].getsockname()[1]

    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    conn = Connection(reader, writer, max_frame_payload=65536)
    rpc = RpcClient(conn)
    conn.on_frame = rpc.handle_frame
    read_task = asyncio.create_task(conn.run())

    try:
        response = await rpc.call(msg_type=0x01, payload=b"PING", timeout=1.0)
        assert response == b"OK"
    finally:
        read_task.cancel()
        await conn.close()
        server.server.close()
        await server.server.wait_closed()
