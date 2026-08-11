"""Atomic writes and stage fingerprints."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import tempfile
from datetime import datetime, timezone
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


def sha256_json(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def atomic_write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".csv", dir=path.parent, delete=False, encoding="utf-8", newline=""
    ) as handle:
        temporary = Path(handle.name)
        frame.to_csv(handle, index=False)
    os.replace(temporary, path)


def atomic_write_json(value: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", dir=path.parent, delete=False, encoding="utf-8"
    ) as handle:
        temporary = Path(handle.name)
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def atomic_save_npy(array: Any, path: Path) -> None:
    import numpy as np

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", suffix=".npy", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        np.save(handle, array, allow_pickle=False)
    os.replace(temporary, path)


def atomic_save_npz(path: Path, **arrays: Any) -> None:
    import numpy as np

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", suffix=".npz", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        np.savez_compressed(handle, **arrays)
    os.replace(temporary, path)


def environment_manifest() -> Dict[str, object]:
    packages = {}
    for name in ("numpy", "pandas", "scikit-learn", "umap-learn"):
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            packages[name] = "not-installed"
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": packages,
    }


def refuse_stale_outputs(manifest_path: Path, expected: Dict[str, object], force: bool) -> bool:
    if manifest_path.exists():
        try:
            with manifest_path.open(encoding="utf-8") as handle:
                current = json.load(handle).get("inputs") == expected
        except (OSError, json.JSONDecodeError):
            current = False
        if current and not force:
            return True
        if not force:
            raise RuntimeError(
                f"Existing transition outputs are stale: {manifest_path}. Use --force for this stage."
            )
    return False
