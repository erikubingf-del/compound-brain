#!/usr/bin/env python3
"""Install or refresh the compound-brain managed block in ~/.codex/AGENTS.md."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

try:
    from scripts.lib.codex_bootstrap import apply_managed_codex_block
    from scripts.lib.codex_automations import ensure_managed_automations
except ModuleNotFoundError:
    from lib.codex_bootstrap import apply_managed_codex_block
    from lib.codex_automations import ensure_managed_automations


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


def infer_repo_root(cli_repo_root: str | None) -> Path:
    if cli_repo_root:
        return Path(cli_repo_root).expanduser().resolve()
    override = os.environ.get("COMPOUND_BRAIN_REPO_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path.cwd().resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Codex with the compound-brain managed runtime block.")
    parser.add_argument("--repo-root", help="Path to the compound-brain repo checkout used for Codex automations")
    args = parser.parse_args()
    agents_path = codex_home_dir() / "AGENTS.md"
    apply_managed_codex_block(agents_path, claude_home_dir())
    automations = ensure_managed_automations(
        codex_home=codex_home_dir(),
        claude_home=claude_home_dir(),
        repo_root=infer_repo_root(args.repo_root),
    )
    print(
        "compound-brain Codex runtime ready at "
        + f"{agents_path} with {len(automations)} managed automation(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
