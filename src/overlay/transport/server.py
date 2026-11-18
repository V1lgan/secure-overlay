import asyncio
import logging
from typing import Callable, Awaitable
from overlay.protocol.frame import Frame
from overlay.transport.connection import Connection

log = logging.getLogger(__name__)

class Server:
    def __init__(self, max_frame_payload: int, on_frame: Callable[[Connection, Frame], Awaitable[None]]):
        self.max_frame_payload = max_frame_payload
        self.on_frame = on_frame
        self.server = None

    async def start(self, host: str, port: int) -> None:
        self.server = await asyncio.start_server(self._handle_client, host, port)
        log.info(f"Server started on {host}:{port}")

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        # Создаем обертку Connection для каждого клиента
        conn = Connection(
            reader, writer, 
            max_frame_payload=self.max_frame_payload,
            on_frame=lambda f: self.on_frame(conn, f)
        )
        await conn.run()
