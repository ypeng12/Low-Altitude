"""Configuration loading and repository-relative path resolution."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Union


@dataclass(frozen=True)
class ProjectConfig:
    raw: Dict[str, Any]
    config_path: Path
    repository_root: Path

    @classmethod
    def load(cls, path: Union[str, Path]) -> "ProjectConfig":
        config_path = Path(path).expanduser().resolve()
        with config_path.open(encoding="utf-8") as handle:
            raw = json.load(handle)
        root = (config_path.parent / raw["repository_root"]).resolve()
        return cls(raw=raw, config_path=config_path, repository_root=root)

    def input_path(self, name: str) -> Path:
        return (self.repository_root / self.raw["inputs"][name]).resolve()

    @property
    def output_dir(self) -> Path:
        return (self.repository_root / self.raw["output_dir"]).resolve()
