# Secure Overlay

Курсовая работа по теме «Защищённая оверлейная сеть передачи данных на основе пиринговых протоколов».

## Текущий статус
Реализован Этап 1: Базовый транспорт.
* 24-байтовый заголовок кадра.
* Потоковый декодер (FrameBuffer) с защитой от превышения размера.
* TCP-сервер и клиент на asyncio.
* Корреляция RPC по request_id.

## Требования
* Python 3.11+
* Linux (WSL)

## Установка
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
'''

## Тестирование

'''bash
pytest -v'''

## Проверка TCP-взаимодействия

Терминал 1 (Сервер):

'''bash
python scripts/ping_server.py'''

Терминал 2 (Клиент):

'''bash
python scripts/ping_client.py'''
