#!/usr/bin/env python3
"""Validate exact-token AI proposals for one emotion-lexicon stage."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_ROOT / "src"))

from emotion_lexicon.ai_review import ingest_stage_responses
from emotion_lexicon.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--responses", type=Path, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    result = ingest_stage_responses(
        config.output_dir / f"stage_{args.stage}",
        args.stage,
        args.responses.resolve(),
        set(config.raw["annotation"]["allowed_statuses"]),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
