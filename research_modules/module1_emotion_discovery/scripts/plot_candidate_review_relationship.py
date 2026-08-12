#!/usr/bin/env python3
"""Plot descriptive review relationships for the provisional Module 1 candidates."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_ROOT / "src"))

from emotion_discovery.candidate_review_relationship import run_candidate_review_relationship
from emotion_discovery.config import default_config_path, load_config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(default_config_path()))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    result = run_candidate_review_relationship(load_config(args.config), force=args.force)
    print(result)


if __name__ == "__main__":
    main()
