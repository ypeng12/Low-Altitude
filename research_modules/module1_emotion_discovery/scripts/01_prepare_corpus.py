#!/usr/bin/env python3
"""Prepare and audit the English review span corpus."""

from pathlib import Path
import sys

MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_ROOT / "src"))

from emotion_discovery.cli import main


if __name__ == "__main__":
    sys.argv.insert(1, "prepare")
    main()
