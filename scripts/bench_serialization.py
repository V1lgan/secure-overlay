import json
import msgpack
import time

# Тестовые данные, которые мы будем сериализовать
payload = {
    "node_id": "a1b2c3d4e5f6g7h8i9j0",
    "ip": "192.168.1.100",
    "port": 9001,
    "timestamp": 1700000000,
    "contacts": [
        {"id": "node1", "ip": "10.0.0.1", "port": 8001},
        {"id": "node2", "ip": "10.0.0.2", "port": 8002},
        {"id": "node3", "ip": "10.0.0.3", "port": 8003},
    ],
    "metadata": {"version": 1, "ttl": 3600}
}

def benchmark(name, encode_func, decode_func, iterations=10000):
    # Замер размера
    encoded = encode_func(payload)
    size_bytes = len(encoded)

    # Замер скорости кодирования/декодирования
    start = time.perf_counter()
    for _ in range(iterations):
        enc = encode_func(payload)
        dec = decode_func(enc)
    end = time.perf_counter()
    
    total_time = end - start
    ops_per_sec = iterations / total_time
    
    return size_bytes, ops_per_sec

def main():
    print(f"{'Формат':<15} | {'Размер (байт)':<15} | {'Скорость (оп/сек)':<20}")
    print("-" * 55)

    # JSON
    json_size, json_speed = benchmark(
        "JSON",
        lambda x: json.dumps(x).encode('utf-8'),
        lambda x: json.loads(x.decode('utf-8'))
    )
    print(f"{'JSON':<15} | {json_size:<15} | {json_speed:,.0f}")

    # MessagePack
    msgpack_size, msgpack_speed = benchmark(
        "MessagePack",
        lambda x: msgpack.packb(x, use_bin_type=True),
        lambda x: msgpack.unpackb(x, raw=False)
    )
    print(f"{'MessagePack':<15} | {msgpack_size:<15} | {msgpack_speed:,.0f}")

    print("\nВывод: MessagePack компактнее JSON на",
          f"{100 - (msgpack_size / json_size * 100):.1f}%")

if __name__ == "__main__":
    main()
