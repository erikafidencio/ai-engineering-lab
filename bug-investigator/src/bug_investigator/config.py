from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


def project_root() -> Path:
    env = os.getenv("BUG_INVESTIGATOR_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[2]


@dataclass
class AppConfig:
    raw: dict[str, Any]
    config_path: Path
    data_dir: Path
    project_root: Path

    @classmethod
    def load(cls, config_path: str | Path | None = None) -> AppConfig:
        root = project_root()
        path = Path(config_path or os.getenv("BUG_INVESTIGATOR_CONFIG", root / "config.yaml"))
        if not path.is_absolute():
            path = root / path
        with path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)
        data_dir = Path(os.getenv("BUG_INVESTIGATOR_DATA_DIR", root / "data"))
        if not data_dir.is_absolute():
            data_dir = root / data_dir
        data_dir.mkdir(parents=True, exist_ok=True)
        return cls(raw=raw, config_path=path, data_dir=data_dir, project_root=root)

    def get(self, *keys: str, default: Any = None) -> Any:
        node: Any = self.raw
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    def resolve_path(self, rel: str) -> Path:
        path = Path(rel)
        if path.is_absolute():
            return path
        return self.project_root / path
