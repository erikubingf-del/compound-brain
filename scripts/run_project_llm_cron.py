#!/usr/bin/env python3
"""Dispatch repo-local scheduled LLM hooks for activated projects."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

try:
    from scripts.lib.department_cycle import run_department_cycle
    from scripts.lib.promotion_inbox import PromotionInbox
    from scripts.lib.skill_evolution import promote_skill_pattern
except ModuleNotFoundError:
    from lib.department_cycle import run_department_cycle
    from lib.promotion_inbox import PromotionInbox
    from lib.skill_evolution import promote_skill_pattern


def claude_home_dir() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".claude"


REGISTRY_PATH = claude_home_dir() / "registry" / "activated-projects.json"


def load_registry() -> list[dict]:
    if not REGISTRY_PATH.exists():
        return []
    data = json.loads(REGISTRY_PATH.read_text())
    return list(data.get("projects", []))


def enabled_departments(project_dir: Path) -> list[str]:
    settings_path = project_dir / ".claude" / "settings.local.json"
    if not settings_path.exists():
        return []

    settings = json.loads(settings_path.read_text())
    departments = settings.get("enabledDepartments")
    if isinstance(departments, list) and departments:
        return [str(item) for item in departments]
    departments_dir = project_dir / ".claude" / "departments"
    if departments_dir.exists():
        return sorted(path.stem for path in departments_dir.glob("*.md"))
    return []


def run_project_cron(project_dir: Path, dry_run: bool = False) -> tuple[str, int]:
    departments = enabled_departments(project_dir)
    if not departments:
        return ("missing enabled departments", 0)

    if dry_run:
        return (f"[dry-run] {', '.join(departments)}", 0)

    results = [run_department_cycle(project_dir, department) for department in departments]
    inbox = PromotionInbox(claude_home_dir() / "knowledge" / "promotions")
    for result in results:
        if result.get("skill_promotion"):
            promote_skill_pattern(
                repo=project_dir,
                skill_name=str(result["skill_promotion"]["skill_name"]),
                related_projects=[project_dir.name],
                key_knowledge=str(result["skill_promotion"]["key_knowledge"]),
                next_improvements=str(result["skill_promotion"]["next_improvements"]),
                pattern_body=str(result["skill_promotion"]["pattern_body"]),
            )
        if result.get("cross_project_candidate"):
            candidate = result["cross_project_candidate"]
            inbox.submit_candidate(
                source_repo=project_dir.name,
                title=str(candidate["title"]),
                summary=str(candidate["summary"]),
                target_kind=str(candidate["target_kind"]),
            )
    summary = ", ".join(
        f"{result['department']}={result['status']}" for result in results
    )
    return (summary or "ok", 0)


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
