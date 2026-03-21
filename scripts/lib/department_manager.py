from __future__ import annotations

from pathlib import Path

from .action_queue import format_ranked_actions


def write_project_action_queue(project_dir: Path, project_name: str, ranked_actions: list[dict]) -> None:
    if not (project_dir / ".brain").exists():
        return
    state_dir = project_dir / ".brain" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / "action-queue.md"
    path.write_text(
        f"# Action Queue — {project_name}\n\n## Ranked Actions\n\n"
        + format_ranked_actions(ranked_actions)
        + "\n"
    )


def write_ranked_department_actions(project_dir: Path, ranked_actions: list[dict]) -> None:
    if not (project_dir / ".claude").exists():
        return
    departments_dir = project_dir / ".claude" / "departments"
    departments_dir.mkdir(parents=True, exist_ok=True)

    grouped: dict[str, list[dict]] = {}
    for action in ranked_actions:
        department = str(action.get("department", "architecture"))
        grouped.setdefault(department, []).append(action)

    for department, actions in grouped.items():
        path = departments_dir / f"{department}.md"
        if path.exists():
            base = path.read_text().split("## Ranked Actions")[0].rstrip()
        else:
            base = f"# {department}\n"
        content = (
            base
            + "\n\n## Ranked Actions\n\n"
            + format_ranked_actions(actions)
            + "\n"
        )
        path.write_text(content)
