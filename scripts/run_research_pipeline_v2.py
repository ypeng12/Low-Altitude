#!/usr/bin/env python3
"""Single restartable entry point for canonical v2 and Module 1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ROOT = REPOSITORY_ROOT / "research_modules" / "canonical_pipeline_v2"
MODULE1_ROOT = REPOSITORY_ROOT / "research_modules" / "module1_emotion_discovery"
sys.path.insert(0, str(CANONICAL_ROOT / "src"))
sys.path.insert(0, str(MODULE1_ROOT / "src"))

from canonical_pipeline.build import run_build
from canonical_pipeline.config import ProjectConfig as CanonicalConfig
from emotion_discovery.clustering import run_clustering
from emotion_discovery.config import load_config as load_module1_config
from emotion_discovery.embeddings import run_embeddings
from emotion_discovery.focused_discovery import run_focused_discovery
from emotion_discovery.goemotions_reference import run_goemotions_reference
from emotion_discovery.handoff import validate_canonical_handoff
from emotion_discovery.prepare import run_prepare
from emotion_discovery.reporting import run_reporting
from emotion_discovery.review_packet import run_review_packet


STAGE_ORDER = (
    "canonical",
    "prepare",
    "embed",
    "handoff",
    "cluster",
    "report",
    "focused",
    "reference",
    "review",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=["all", *STAGE_ORDER], default="all")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--canonical-config",
        default=str(CANONICAL_ROOT / "config" / "default.json"),
    )
    parser.add_argument(
        "--module1-config",
        default=str(MODULE1_ROOT / "config" / "default.json"),
    )
    arguments = parser.parse_args()

    canonical_config = CanonicalConfig.load(arguments.canonical_config)
    module1_config = load_module1_config(arguments.module1_config)
    functions = {
        "canonical": lambda: run_build(canonical_config, force=arguments.force),
        "prepare": lambda: run_prepare(module1_config, force=arguments.force),
        "embed": lambda: run_embeddings(module1_config, force=arguments.force),
        "handoff": lambda: validate_canonical_handoff(module1_config),
        "cluster": lambda: run_clustering(module1_config, force=arguments.force),
        "report": lambda: run_reporting(module1_config, force=arguments.force),
        "focused": lambda: run_focused_discovery(module1_config, force=arguments.force),
        "reference": lambda: run_goemotions_reference(module1_config, force=arguments.force),
        "review": lambda: run_review_packet(module1_config, force=arguments.force),
    }
    selected = STAGE_ORDER if arguments.only == "all" else (arguments.only,)
    for stage in selected:
        result = functions[stage]()
        print(json.dumps({stage: result}, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
