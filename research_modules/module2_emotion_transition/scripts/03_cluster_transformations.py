#!/usr/bin/env python3
"""Cluster directional source-to-target semantic vectors."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_ROOT / "src"))

from emotion_transition.clustering import run_clustering
from emotion_transition.config import default_config_path, load_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(default_config_path()))
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args()
    result = run_clustering(load_config(arguments.config), force=arguments.force)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
