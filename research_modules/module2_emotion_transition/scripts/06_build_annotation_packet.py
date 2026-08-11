#!/usr/bin/env python3
"""Build blinded, double-coded AEM and Transition annotation sheets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_ROOT / "src"))

from emotion_transition.annotation_packet import run_annotation_packet
from emotion_transition.config import default_config_path, load_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(default_config_path()))
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args()
    result = run_annotation_packet(load_config(arguments.config), force=arguments.force)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
