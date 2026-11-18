import asyncio
import logging
from overlay.config import load_config
from overlay.protocol.frame import Frame, IS_RESPONSE
from overlay.transport.server import Server

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def handle_ping(conn, frame: Frame):
    print(f"Server got frame type=0x{frame.type:02x}, payload={frame.payload}")
    # Отправляем PONG (0x02), возвращая тот же request_id и флаг IS_RESPONSE
    response = Frame(
        version=frame.version,
        type=0x02, 
        flags=IS_RESPONSE,
        request_id=frame.request_id,
        payload=b"PONG"
    )
    await conn.send_frame(response)

async def main():
    cfg = load_config("configs/node_a.yaml")
    server = Server(
        max_frame_payload=cfg.protocol.max_frame_payload,
        on_frame=handle_ping
    )
    await server.start(cfg.node.host, cfg.node.port)
    await asyncio.Event().wait() # Работает вечно

if __name__ == "__main__":
    asyncio.run(main())
