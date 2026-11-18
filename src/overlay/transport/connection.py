import asyncio
import logging
from typing import Awaitable, Callable

from overlay.protocol.frame import Frame, HEADER_SIZE
from overlay.protocol.stream import FrameBuffer

log = logging.getLogger(__name__)

class Connection:
    def __init__(
        self, 
        reader: asyncio.StreamReader, 
        writer: asyncio.StreamWriter, 
        max_frame_payload: int,
        on_frame: Callable[[Frame], Awaitable[None]] | None = None
    ):
        self.reader = reader
        self.writer = writer
        self.max_frame_payload = max_frame_payload
        self.on_frame = on_frame
        self._buffer = FrameBuffer(max_frame_payload)
        self._is_closed = False

    async def send_frame(self, frame: Frame) -> None:
        if self._is_closed:
            raise ConnectionError("Connection is closed")
        try:
            self.writer.write(frame.encode())
            await self.writer.drain()
        except Exception as e:
            self._is_closed = True
            raise ConnectionError(f"Failed to send frame: {e}")

    async def run(self) -> None:
        """Читает из сокета и передает готовые кадры в on_frame."""
        try:
            while not self._is_closed:
                data = await self.reader.read(4096)
                if not data:
                    break  # Соединение закрыто другой стороной
                
                frames = self._buffer.feed(data)
                for frame in frames:
                    if self.on_frame:
                        await self.on_frame(frame)
        except ValueError as e:
            # Ловим ошибку превышения лимита из FrameBuffer
            log.warning(f"Protocol error: {e}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            log.error(f"Connection error: {e}")
        finally:
            await self.close()

    async def close(self) -> None:
        if not self._is_closed:
            self._is_closed = True
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception:
                pass
