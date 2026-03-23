#!/usr/bin/env python3
"""Refresh the global compound-brain GitHub skill radar."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

try:
    from scripts.lib.skill_radar import refresh_skill_radar
except ModuleNotFoundError:
    from lib.skill_radar import refresh_skill_radar


def claude_home_dir() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".claude"


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh compound-brain external skill radar.")
    parser.add_argument("--project-dir", action="append", help="Optional project dir to scope the refresh")
    parser.add_argument("--json-output", action="store_true", help="Emit JSON summary on stdout")
    args = parser.parse_args()

    project_dirs = [Path(item).resolve() for item in (args.project_dir or [])]
    result = refresh_skill_radar(
        claude_home=claude_home_dir(),
        project_dirs=project_dirs or None,
    )
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(
            "skill-radar refreshed: "
            + f"{len(result['skill_catalog']['candidates'])} candidates, "
            + f"{len(result['project_tip_catalog']['tips'])} tips"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
