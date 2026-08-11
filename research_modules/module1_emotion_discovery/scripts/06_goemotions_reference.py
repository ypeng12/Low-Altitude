#!/usr/bin/env python3
"""Profile cluster representatives with pinned GoEmotions probabilities."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_ROOT / "src"))

from emotion_discovery.config import default_config_path, load_config
from emotion_discovery.goemotions_reference import run_goemotions_reference


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(default_config_path()))
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args()
    result = run_goemotions_reference(load_config(arguments.config), force=arguments.force)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
