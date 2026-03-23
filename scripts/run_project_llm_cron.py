#!/usr/bin/env python3
"""Dispatch repo-local scheduled LLM hooks for activated projects."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

try:
    from scripts.lib.autoresearch_runner import run_autoresearch_cycle
    from scripts.lib.department_cycle import run_department_cycle
    from scripts.lib.promotion_inbox import PromotionInbox
    from scripts.lib.skill_inventory import refresh_repo_skill_state
    from scripts.lib.skill_evolution import promote_skill_pattern
except ModuleNotFoundError:
    from lib.autoresearch_runner import run_autoresearch_cycle
    from lib.department_cycle import run_department_cycle
    from lib.promotion_inbox import PromotionInbox
    from lib.skill_inventory import refresh_repo_skill_state
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


def run_project_cron(
    project_dir: Path,
    dry_run: bool = False,
    refresh_skills: bool = True,
    current_depth: int | None = None,
    lead_department: str | None = None,
    supporting_departments: list[str] | None = None,
    skill_state: dict[str, object] | None = None,
    top_action: str | None = None,
    goal: str | None = None,
) -> tuple[str, int]:
    departments = enabled_departments(project_dir)
    if not departments:
        return ("missing enabled departments", 0)

    if dry_run:
        return (f"[dry-run] {', '.join(departments)}", 0)

    if refresh_skills or skill_state is None:
        skill_state = refresh_repo_skill_state(project_dir, claude_home=claude_home_dir())

    if current_depth is not None and current_depth <= 2:
        summary = "planning-only"
        if skill_state is not None:
            summary += f" skills=active:{len(skill_state['active'])}/missing:{len(skill_state['missing'])}"
        return (summary, 0)

    selected_departments = list(departments)
    if lead_department:
        selected_departments = [lead_department]
        for item in supporting_departments or []:
            if item in departments and item not in selected_departments:
                selected_departments.append(item)

    results: list[dict[str, object]] = []
    if selected_departments:
        primary_department = selected_departments[0]
        support = selected_departments[1:]
        primary_result = run_department_cycle(
            project_dir,
            primary_department,
            current_depth=current_depth or 3,
            goal=goal or "",
            top_action=top_action,
            supporting_departments=support,
            skill_state=skill_state or {"active": [], "missing": []},
        )
        results.append(primary_result)
        for department in primary_result.get("handoff_departments", []):
            if department in support:
                results.append(
                    run_department_cycle(
                        project_dir,
                        str(department),
                        current_depth=current_depth or 3,
                        goal=goal or "",
                        top_action=f"Verify handoff for {primary_result['action']}",
                        supporting_departments=[],
                        skill_state=skill_state or {"active": [], "missing": []},
                    )
                )
    autoresearch_program = project_dir / ".brain" / "autoresearch" / "program.md"
    if autoresearch_program.exists() and (current_depth is None or current_depth >= 4):
        research_department = "research" if "research" in selected_departments else selected_departments[0]
        autoresearch_result = run_autoresearch_cycle(project_dir, research_department)
        results.append(
            {
                "department": "autoresearch",
                "status": autoresearch_result["status"],
                "reason": autoresearch_result.get("reason", ""),
            }
        )
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
            details = {
                key: value
                for key, value in candidate.items()
                if key not in {"title", "summary", "target_kind"}
            }
            inbox.submit_candidate(
                source_repo=project_dir.name,
                title=str(candidate["title"]),
                summary=str(candidate["summary"]),
                target_kind=str(candidate["target_kind"]),
                details=details or None,
            )
    parts: list[str] = []
    if skill_state is not None:
        parts.append(
            "skills="
            + f"active:{len(skill_state['active'])}"
            + f"/missing:{len(skill_state['missing'])}"
        )
    parts.extend(
        f"{result['department']}={result['status']}" for result in results
    )
    summary = ", ".join(parts)
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
