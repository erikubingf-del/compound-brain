#!/usr/bin/env python3
"""Install or refresh the compound-brain managed block in ~/.codex/AGENTS.md."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

try:
    from scripts.lib.codex_bootstrap import apply_managed_codex_block
except ModuleNotFoundError:
    from lib.codex_bootstrap import apply_managed_codex_block


def codex_home_dir() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_CODEX_HOME")
    if override:
        return Path(override)
    return Path.home() / ".codex"


def claude_home_dir() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".claude"


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Codex with the compound-brain managed runtime block.")
    parser.parse_args()
    agents_path = codex_home_dir() / "AGENTS.md"
    apply_managed_codex_block(agents_path, claude_home_dir())
    print(f"compound-brain Codex runtime ready at {agents_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
