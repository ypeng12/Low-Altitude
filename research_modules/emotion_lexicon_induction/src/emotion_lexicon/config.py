"""Configuration loading and repository-relative path resolution."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LexiconConfig:
    raw: dict[str, Any]
    config_path: Path
    repository_root: Path

    def input_path(self, name: str) -> Path:
        return (self.repository_root / self.raw["inputs"][name]).resolve()

    @property
    def output_dir(self) -> Path:
        return (self.repository_root / self.raw["output_dir"]).resolve()


def load_config(path: Path) -> LexiconConfig:
    path = path.resolve()
    raw = json.loads(path.read_text(encoding="utf-8"))
    repository_root = (path.parent / raw["repository_root"]).resolve()
    if not repository_root.is_dir():
        raise FileNotFoundError(f"Repository root does not exist: {repository_root}")
    for input_name, relative in raw["inputs"].items():
        input_path = (repository_root / relative).resolve()
        if not input_path.is_file():
            raise FileNotFoundError(f"Missing input {input_name}: {input_path}")
    return LexiconConfig(raw=raw, config_path=path, repository_root=repository_root)
