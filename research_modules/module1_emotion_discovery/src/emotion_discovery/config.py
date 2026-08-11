"""Configuration loading and path validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass(frozen=True)
class ProjectConfig:
    """Loaded JSON configuration with resolved project paths."""

    path: Path
    raw: Dict[str, Any]
    repository_root: Path
    module_root: Path
    output_dir: Path

    def input_path(self, name: str) -> Path:
        try:
            relative = self.raw["inputs"][name]
        except KeyError as exc:
            raise KeyError(f"Missing configured input: {name}") from exc
        return (self.repository_root / relative).resolve()

    @property
    def random_seed(self) -> int:
        return int(self.raw["random_seed"])


def load_config(path: str | Path) -> ProjectConfig:
    """Load a config file and resolve all roots relative to that file."""

    config_path = Path(path).expanduser().resolve()
    with config_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    repository_root = (config_path.parent / raw["repository_root"]).resolve()
    module_root = config_path.parent.parent.resolve()
    output_dir = (repository_root / raw["output_dir"]).resolve()

    if not repository_root.is_dir():
        raise FileNotFoundError(f"Repository root does not exist: {repository_root}")
    for input_name, relative_path in raw["inputs"].items():
        input_path = (repository_root / relative_path).resolve()
        if not input_path.is_file():
            raise FileNotFoundError(f"Input '{input_name}' does not exist: {input_path}")

    input_paths = {
        (repository_root / relative_path).resolve()
        for relative_path in raw["inputs"].values()
    }
    if output_dir in input_paths:
        raise ValueError("Output directory may not point to an input file")

    return ProjectConfig(
        path=config_path,
        raw=raw,
        repository_root=repository_root,
        module_root=module_root,
        output_dir=output_dir,
    )


def default_config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "default.json"
