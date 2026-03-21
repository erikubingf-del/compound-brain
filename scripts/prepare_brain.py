#!/usr/bin/env python3
"""Prepare static project memory without enabling repo-local autonomy."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

try:
    from scripts.materialize_project_claude import materialize_prepared_project
except ModuleNotFoundError:
    from materialize_project_claude import materialize_prepared_project


SCRIPT_DIR = Path(__file__).resolve().parent


def prepare_brain(repo: Path) -> None:
    repo = repo.resolve()
    setup_script = SCRIPT_DIR / "setup_brain.sh"
    subprocess.run(
        ["bash", str(setup_script), str(repo), repo.name],
        capture_output=True,
        text=True,
        check=True,
    )
    materialize_prepared_project(repo)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare a static project brain by writing CLAUDE.md, .brain/, and "
            ".codex/AGENTS.md without enabling repo-local autonomy."
        )
    )
    parser.add_argument("project_dir", nargs="?", default=".", help="Repo path to prepare")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    prepare_brain(Path(args.project_dir))
    print("compound-brain prepare-brain complete")
    print(f"repo: {Path(args.project_dir).resolve()}")
    print("created: CLAUDE.md, .brain/, .codex/AGENTS.md")
    print("next state: prepared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

