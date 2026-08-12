"""Command-line interface for staged unigram lexicon induction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_config
from .pipeline import build_stage


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--config", type=Path, required=True)
    result.add_argument("--stage", default="discovery_500")
    return result


def main() -> None:
    args = parser().parse_args()
    summary = build_stage(load_config(args.config), args.stage)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
