"""Command-line entry point for restartable Module 1 stages."""

from __future__ import annotations

import argparse
import json
import random
from typing import Callable, Dict

import numpy as np

from .clustering import run_clustering
from .config import default_config_path, load_config
from .embeddings import run_embeddings
from .focused_discovery import run_focused_discovery
from .goemotions_reference import run_goemotions_reference
from .handoff import validate_canonical_handoff
from .prepare import run_prepare
from .reporting import run_reporting
from .review_packet import run_review_packet


def run_handoff(config, force: bool = False):
    del force
    return validate_canonical_handoff(config)


STAGES: Dict[str, Callable] = {
    "prepare": run_prepare,
    "embed": run_embeddings,
    "handoff": run_handoff,
    "cluster": run_clustering,
    "report": run_reporting,
    "focused": run_focused_discovery,
    "reference": run_goemotions_reference,
    "review": run_review_packet,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage",
        choices=[*STAGES, "all"],
        help="Run one stage or all stages in dependency order",
    )
    parser.add_argument(
        "--config",
        default=str(default_config_path()),
        help="Path to a JSON configuration file",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace stale outputs only inside this module's output directory",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)
    random.seed(config.random_seed)
    np.random.seed(config.random_seed)
    selected = list(STAGES) if args.stage == "all" else [args.stage]
    results = {}
    for stage in selected:
        results[stage] = STAGES[stage](config, force=args.force)
        print(json.dumps({stage: results[stage]}, indent=2, default=str))


if __name__ == "__main__":
    main()
