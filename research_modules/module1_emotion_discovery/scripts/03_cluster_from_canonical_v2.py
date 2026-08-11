#!/usr/bin/env python3
"""Validate canonical v2 alignment, then run Module 1 clustering."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_ROOT / "src"))

from emotion_discovery.clustering import run_clustering
from emotion_discovery.config import default_config_path, load_config
from emotion_discovery.handoff import validate_canonical_handoff


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(default_config_path()))
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args()
    config = load_config(arguments.config)
    print(json.dumps({"canonical_handoff": validate_canonical_handoff(config)}, indent=2))
    print(json.dumps({"cluster": run_clustering(config, force=arguments.force)}, indent=2, default=str))


if __name__ == "__main__":
    main()
