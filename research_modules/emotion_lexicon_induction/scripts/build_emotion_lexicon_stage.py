#!/usr/bin/env python3
"""Repository-friendly wrapper for the emotion lexicon package CLI."""

from __future__ import annotations

import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_ROOT / "src"))

from emotion_lexicon.cli import main


if __name__ == "__main__":
    main()
