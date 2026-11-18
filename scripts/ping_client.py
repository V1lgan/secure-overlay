import asyncio
import logging
from overlay.config import load_config
from overlay.transport.connection import Connection
from overlay.transport.rpc import RpcClient
from overlay.protocol.frame import Frame

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def main():
    cfg = load_config("configs/node_b.yaml")
    
    # Подключаемся к серверу (порт из node_a)
    reader, writer = await asyncio.open_connection("127.0.0.1", 9001)
    conn = Connection(reader, writer, max_frame_payload=cfg.protocol.max_frame_payload)
    
    rpc = RpcClient(conn)
    # Перехватываем входящие кадры и скармливаем их RPC-клиенту
    conn.on_frame = rpc.handle_frame

    # Запускаем чтение сокета в фоне
    read_task = asyncio.create_task(conn.run())

    try:
        for i in range(5):
            print(f"Sending PING {i+1}...")
            # PING = 0x01
            response_payload = await rpc.call(msg_type=0x01, payload=b"PING", timeout=2.0)
            print(f"Got response: {response_payload.decode()}")
            await asyncio.sleep(1)
    finally:
        read_task.cancel()
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
