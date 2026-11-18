from __future__ import annotations

from .frame import HEADER_SIZE, Frame, decode_header


class FrameBuffer:
    def __init__(self, max_frame_payload: int):
        self.max_frame_payload = max_frame_payload
        self._buffer = bytearray()

    def feed(self, data: bytes) -> list[Frame]:
        """Принимает порцию байтов из TCP, возвращает список готовых кадров."""
        self._buffer.extend(data)
        frames = []

        while True:
            # 1. Ждем, пока накопится хотя бы 24 байта заголовка
            if len(self._buffer) < HEADER_SIZE:
                break

            # 2. Пытаемся прочитать заголовок
            header_bytes = self._buffer[:HEADER_SIZE]
            header = decode_header(header_bytes)

            # 3. E1-6: Проверка лимита ДО выделения памяти под payload
            if header.payload_length > self.max_frame_payload:
                # Сбрасываем буфер и кидаем ошибку, чтобы закрыть соединение
                self._buffer.clear()
                raise ValueError(
                    f"Payload length {header.payload_length} exceeds "
                    f"max limit {self.max_frame_payload}"
                )

            frame_size = HEADER_SIZE + header.payload_length
            
            # 4. Ждем, пока накопится весь payload
            if len(self._buffer) < frame_size:
                break

            # 5. Кадр полностью в буфере, извлекаем его
            payload = bytes(self._buffer[HEADER_SIZE:frame_size])
            frame = Frame(
                version=header.version,
                type=header.type,
                flags=header.flags,
                request_id=header.request_id,
                payload=payload,
            )
            frames.append(frame)

            # 6. Удаляем прочитанные байты из буфера и идем дальше
            del self._buffer[:frame_size]

        return frames
