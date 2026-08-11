"""Command-line entry point."""

from __future__ import annotations

import argparse
import json

from .build import run_build
from .config import ProjectConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the canonical v2 research dataset")
    parser.add_argument("--config", required=True)
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args()
    result = run_build(ProjectConfig.load(arguments.config), force=arguments.force)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
