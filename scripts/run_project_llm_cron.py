#!/usr/bin/env python3
"""Dispatch repo-local scheduled LLM hooks for activated projects."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


REGISTRY_PATH = Path.home() / ".claude" / "registry" / "activated-projects.json"


def load_registry() -> list[dict]:
    if not REGISTRY_PATH.exists():
        return []
    data = json.loads(REGISTRY_PATH.read_text())
    return list(data.get("projects", []))


def run_project_cron(project_dir: Path, dry_run: bool = False) -> tuple[str, int]:
    settings_path = project_dir / ".claude" / "settings.local.json"
    if not settings_path.exists():
        return ("missing settings.local.json", 0)

    settings = json.loads(settings_path.read_text())
    command = settings.get("llmCron", {}).get("command")
    if not command:
        return ("missing llmCron.command", 0)

    if dry_run:
        return (f"[dry-run] {command}", 0)

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        cwd=str(project_dir),
        check=False,
    )
    if result.returncode == 0:
        return (result.stdout.strip() or "ok", 0)
    return (result.stderr.strip() or "failed", result.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repo-local LLM cron hooks for alive repos.")
    parser.add_argument("--project-dir", help="Run a single project only")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without running them")
    args = parser.parse_args()

    if args.project_dir:
        projects = [{"repo_path": str(Path(args.project_dir).resolve())}]
    else:
        projects = load_registry()

    for project in projects:
        project_dir = Path(project["repo_path"]).resolve()
        output, rc = run_project_cron(project_dir, dry_run=args.dry_run)
        print(f"[project-llm-cron] {project_dir}: rc={rc} {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
