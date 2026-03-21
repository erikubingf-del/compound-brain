#!/usr/bin/env python3
"""Generate scheduled review artifacts from the global promotion inbox."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

try:
    from scripts.lib.promotion_review import review_pending_candidates
except ModuleNotFoundError:
    from lib.promotion_review import review_pending_candidates


def claude_home_dir() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".claude"


def main() -> int:
    parser = argparse.ArgumentParser(description="Review pending compound-brain promotion candidates.")
    parser.parse_args()
    promotions_root = claude_home_dir() / "knowledge" / "promotions"
    result = review_pending_candidates(promotions_root)
    print(
        "compound-brain promotion review complete: "
        f"{result['reviewed_count']} reviewed -> {result['review_path']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
