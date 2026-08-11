"""Atomic output helpers and reproducibility metadata."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import tempfile
from importlib import metadata
from pathlib import Path
from typing import Any, Dict

import pandas as pd


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".csv", dir=path.parent, delete=False, encoding="utf-8", newline="") as tmp:
        temporary = Path(tmp.name)
        frame.to_csv(tmp, index=False)
    os.replace(temporary, path)


def atomic_write_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".json", dir=path.parent, delete=False, encoding="utf-8") as tmp:
        temporary = Path(tmp.name)
        json.dump(data, tmp, ensure_ascii=False, indent=2, sort_keys=True)
        tmp.write("\n")
    os.replace(temporary, path)


def environment_manifest() -> Dict[str, str]:
    packages = {}
    for name in ("pandas", "openpyxl", "fasttext-wheel"):
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            packages[name] = "not-installed"
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        **packages,
    }
