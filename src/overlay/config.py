from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ProtocolConfig:
    version: int
    max_frame_payload: int


@dataclass(frozen=True)
class TransportConfig:
    connect_timeout: float
    write_timeout: float


@dataclass(frozen=True)
class NodeConfig:
    host: str
    port: int
    state_dir: Path


@dataclass(frozen=True)
class LoggingConfig:
    level: str


@dataclass(frozen=True)
class Config:
    protocol: ProtocolConfig
    transport: TransportConfig
    node: NodeConfig
    logging: LoggingConfig


def load_config(path: str | Path) -> Config:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return Config(
        protocol=ProtocolConfig(**raw["protocol"]),
        transport=TransportConfig(**raw["transport"]),
        node=NodeConfig(**raw["node"]),
        logging=LoggingConfig(**raw["logging"]),
    )
