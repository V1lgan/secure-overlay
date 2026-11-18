from overlay.config import load_config


def test_configs_loaded_from_yaml():
    a = load_config("configs/node_a.yaml")
    b = load_config("configs/node_b.yaml")

    assert a.node.port != b.node.port
    assert a.protocol.max_frame_payload == b.protocol.max_frame_payload == 65536
    assert a.transport.connect_timeout == 5.0


def test_max_frame_payload_changes_via_config(tmp_path):
    cfg_text = """
protocol: {version: 1, max_frame_payload: 1024}
transport: {connect_timeout: 1.0, write_timeout: 1.0}
node: {host: "127.0.0.1", port: 9999, state_dir: "data/tmp"}
logging: {level: "DEBUG"}
"""
    p = tmp_path / "small.yaml"
    p.write_text(cfg_text, encoding="utf-8")
    cfg = load_config(p)
    assert cfg.protocol.max_frame_payload == 1024
