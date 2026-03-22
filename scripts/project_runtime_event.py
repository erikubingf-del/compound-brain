#!/usr/bin/env python3
"""Shared repo event runtime for session hooks and cron-driven autoimprovement."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.project_auditor import audit_project
    from scripts.project_intelligence import run_for_project
    from scripts.probability_engine import ProjectState, rank_actions
    from scripts.run_project_llm_cron import run_project_cron
    from scripts.update_architecture_scorecard import main as update_architecture_scorecard_main
except ModuleNotFoundError:
    from project_auditor import audit_project
    from project_intelligence import run_for_project
    from probability_engine import ProjectState, rank_actions
    from run_project_llm_cron import run_project_cron
    from update_architecture_scorecard import main as update_architecture_scorecard_main


def claude_home_dir() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".claude"


def activation_registry_path() -> Path:
    return claude_home_dir() / "registry" / "activated-projects.json"


def load_registry() -> list[dict[str, Any]]:
    path = activation_registry_path()
    if not path.exists():
        return []
    payload = json.loads(path.read_text())
    return list(payload.get("projects", []))


def is_activated_repo(project_dir: Path) -> bool:
    return (project_dir / ".brain").exists() and (project_dir / ".claude" / "settings.local.json").exists()


def audit_is_due(project_dir: Path, max_age_days: int = 7) -> bool:
    audit_path = project_dir / ".brain" / "knowledge" / "areas" / "project-audit.md"
    if not audit_path.exists():
        return True
    age_days = (datetime.now(timezone.utc).timestamp() - audit_path.stat().st_mtime) / 86400
    return age_days >= max_age_days


def refresh_ranked_actions(project_dir: Path) -> dict[str, Any]:
    state = ProjectState.from_brain(project_dir)
    result = rank_actions(state)
    return {
        "top_action": result.top_action.title,
        "top_action_category": result.top_action.category,
        "goal": result.goal,
    }


def maybe_update_scorecard(project_dir: Path) -> bool:
    if not (project_dir / ".brain" / "architecture" / "evaluator.md").exists():
        return False
    previous_argv = list(os.sys.argv)
    try:
        os.sys.argv = [
            "update_architecture_scorecard.py",
            "--repo-root",
            str(project_dir),
        ]
        update_architecture_scorecard_main()
        return True
    finally:
        os.sys.argv = previous_argv


def run_project_runtime_event(project_dir: Path, event: str) -> dict[str, Any]:
    project_dir = project_dir.resolve()
    if not is_activated_repo(project_dir):
        return {"status": "skipped", "reason": "repo-not-activated", "event": event}

    audit_refreshed = False
    if event in {"session-start", "cron"} and audit_is_due(project_dir):
        audit_refreshed = audit_project(project_dir, force=True)

    brief = run_for_project(project_dir, dry_run=False)
    ranking = refresh_ranked_actions(project_dir)
    runtime: dict[str, Any] = {
        "status": "ok",
        "event": event,
        "audit_refreshed": audit_refreshed,
        "brief_written": bool(brief is not None),
        "top_action": ranking["top_action"],
        "goal": ranking["goal"],
    }

    if event == "cron":
        summary, rc = run_project_cron(project_dir, dry_run=False)
        runtime["cron_summary"] = summary
        runtime["cron_rc"] = rc

    if event == "stop":
        runtime["scorecard_updated"] = maybe_update_scorecard(project_dir)

    return runtime


def main() -> int:
    parser = argparse.ArgumentParser(description="Run compound-brain repo runtime for a hook or cron event.")
    parser.add_argument("--project-dir", help="Single activated project")
    parser.add_argument("--event", choices=["session-start", "stop", "cron"], required=True)
    parser.add_argument("--all-activated", action="store_true", help="Run for all activated projects from the registry")
    args = parser.parse_args()

    if args.all_activated:
        projects = [Path(item["repo_path"]).resolve() for item in load_registry()]
    elif args.project_dir:
        projects = [Path(args.project_dir).resolve()]
    else:
        projects = [Path.cwd().resolve()]

    for project_dir in projects:
        result = run_project_runtime_event(project_dir, args.event)
        print(
            f"[project-runtime:{args.event}] {project_dir}: "
            f"{json.dumps(result, sort_keys=True)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
