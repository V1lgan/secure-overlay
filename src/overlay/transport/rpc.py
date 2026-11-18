import asyncio
import logging
import secrets
from overlay.protocol.frame import Frame, IS_RESPONSE, IS_ERROR
from overlay.transport.connection import Connection

log = logging.getLogger(__name__)

class RequestTimeout(Exception):
    pass

class ConnectionClosed(Exception):
    pass

class RpcClient:
    def __init__(self, conn: Connection):
        self.conn = conn
        self.pending_requests: dict[bytes, asyncio.Future] = {}

    async def call(self, msg_type: int, payload: bytes, timeout: float = 5.0) -> bytes:
        req_id = secrets.token_bytes(16)
        future = asyncio.get_running_loop().create_future()
        self.pending_requests[req_id] = future

        frame = Frame(
            version=1, type=msg_type, flags=0, request_id=req_id, payload=payload
        )
        
        try:
            await self.conn.send_frame(frame)
            # Ждем ответа или тайм-аута
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            raise RequestTimeout(f"Request {req_id.hex()} timed out")
        finally:
            self.pending_requests.pop(req_id, None)

    async def handle_frame(self, frame: Frame) -> None:
        """Вызывается, когда Connection получает кадр."""
        if not (frame.flags & IS_RESPONSE):
            log.warning(f"Received unexpected non-response frame type {frame.type}")
            return

        future = self.pending_requests.get(frame.request_id)
        
        # E1-6: Если будущего нет — это чужой или поздний ответ, отбрасываем.
        if not future:
            log.warning(f"Discarding response with unknown request_id {frame.request_id.hex()}")
            return
            
        if future.done():
            log.warning(f"Discarding duplicate response for {frame.request_id.hex()}")
            return

        if frame.flags & IS_ERROR:
            future.set_exception(RuntimeError(frame.payload.decode('utf-8', 'ignore')))
        else:
            future.set_result(frame.payload)
