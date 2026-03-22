#!/usr/bin/env python3
"""Apply approved promotion candidates into canonical global knowledge."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

try:
    from scripts.lib.promotion_materializer import apply_approved_candidates
except ModuleNotFoundError:
    from lib.promotion_materializer import apply_approved_candidates


def claude_home_dir() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".claude"


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply approved compound-brain promotion candidates.")
    parser.parse_args()
    claude_home = claude_home_dir()
    result = apply_approved_candidates(
        promotions_root=claude_home / "knowledge" / "promotions",
        knowledge_root=claude_home / "knowledge",
    )
    print(
        "compound-brain promotion apply complete: "
        f"{result['applied_count']} applied"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
