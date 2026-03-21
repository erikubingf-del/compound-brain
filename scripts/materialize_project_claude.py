#!/usr/bin/env python3
"""Generate repo-local Claude control surfaces for an activated project."""

from __future__ import annotations

from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates" / "project_claude"


def load_template(relative_path: str, fallback: str) -> str:
    template_path = TEMPLATE_ROOT / relative_path
    if template_path.exists():
        return template_path.read_text()
    return fallback


def render_template(template: str, project_name: str, department_name: str = "") -> str:
    return (
        template.replace("[PROJECT_NAME]", project_name)
        .replace("[DEPARTMENT_NAME]", department_name)
    )


def materialize_project_claude(repo: Path, departments: list[str]) -> None:
    project_name = repo.name
    claude_dir = repo / ".claude"
    hooks_dir = claude_dir / "hooks"
    departments_dir = claude_dir / "departments"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    departments_dir.mkdir(parents=True, exist_ok=True)

    claude_template = load_template(
        "CLAUDE.md",
        "# [PROJECT_NAME]\n\n## Activation Mode\nAlive repo.\n",
    )
    (repo / "CLAUDE.md").write_text(render_template(claude_template, project_name))

    settings_template = load_template(
        "settings.local.json",
        '{\n  "hooks": {\n    "SessionStart": [],\n    "Stop": []\n  }\n}\n',
    )
    (claude_dir / "settings.local.json").write_text(
        render_template(settings_template, project_name)
    )

    for hook_name in [
        "project_session_start.py",
        "project_stop.py",
        "project_llm_cron.py",
    ]:
        fallback = "#!/usr/bin/env python3\nprint('project hook placeholder')\n"
        hook_template = load_template(f"hooks/{hook_name}", fallback)
        (hooks_dir / hook_name).write_text(render_template(hook_template, project_name))

    department_template = load_template(
        "departments/architecture.md",
        "# [DEPARTMENT_NAME]\n\n## Goal\nPending definition.\n",
    )
    for department in departments:
        specific_template = load_template(
            f"departments/{department}.md",
            department_template,
        )
        (departments_dir / f"{department}.md").write_text(
            render_template(specific_template, project_name, department)
        )


if __name__ == "__main__":
    raise SystemExit("Use materialize_project_claude() from activation workflows.")
