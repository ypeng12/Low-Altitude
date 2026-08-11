"""Configuration and path resolution."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class ProjectConfig:
    path: Path
    raw: Dict[str, Any]
    repository_root: Path
    output_dir: Path

    def input_path(self, name: str) -> Path:
        return (self.repository_root / self.raw["inputs"][name]).resolve()

    @property
    def random_seed(self) -> int:
        return int(self.raw["random_seed"])


def load_config(path: str | Path) -> ProjectConfig:
    config_path = Path(path).expanduser().resolve()
    with config_path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    root = (config_path.parent / raw["repository_root"]).resolve()
    for name, relative in raw["inputs"].items():
        source = (root / relative).resolve()
        if not source.is_file():
            raise FileNotFoundError(f"Configured input '{name}' is missing: {source}")
    return ProjectConfig(
        path=config_path,
        raw=raw,
        repository_root=root,
        output_dir=(root / raw["output_dir"]).resolve(),
    )


def default_config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "default.json"
