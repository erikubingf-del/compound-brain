#!/usr/bin/env python3
"""Generate repo-local Claude control surfaces for an activated project."""

from __future__ import annotations

from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates" / "project_claude"
CODEX_TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates" / "project_codex"


def load_template(template_root: Path, relative_path: str, fallback: str) -> str:
    template_path = template_root / relative_path
    if template_path.exists():
        return template_path.read_text()
    return fallback


def render_template(template: str, project_name: str, department_name: str = "") -> str:
    return (
        template.replace("[PROJECT_NAME]", project_name)
        .replace("[DEPARTMENT_NAME]", department_name)
    )


def write_project_claude_md(repo: Path, activation_mode: str) -> None:
    project_name = repo.name
    if activation_mode == "prepared":
        content = (
            f"# {project_name}\n\n"
            "## Brain Mode\n"
            "This repo has a prepared project brain under compound-brain.\n\n"
            "## Control Plane\n"
            "- Project memory lives in `.brain/`\n"
            "- Codex reads `.codex/AGENTS.md`\n"
            "- Repo-local `.claude/` is created only after explicit activation\n\n"
            "## Operating Rule\n"
            "Read `.brain/memory/project_context.md` and `.brain/memory/feedback_rules.md` before project-specific work.\n"
        )
    else:
        claude_template = load_template(
            TEMPLATE_ROOT,
            "CLAUDE.md",
            "# [PROJECT_NAME]\n\n## Activation Mode\nAlive repo.\n",
        )
        content = render_template(claude_template, project_name)
    (repo / "CLAUDE.md").write_text(content)


def materialize_codex_adapter(repo: Path) -> None:
    codex_dir = repo / ".codex"
    codex_dir.mkdir(parents=True, exist_ok=True)
    template = load_template(
        CODEX_TEMPLATE_ROOT,
        "AGENTS.md",
        "# [PROJECT_NAME]\n\nRead `CLAUDE.md` and `.brain/` before project-specific work.\n",
    )
    (codex_dir / "AGENTS.md").write_text(render_template(template, repo.name))


def materialize_prepared_project(repo: Path) -> None:
    write_project_claude_md(repo, activation_mode="prepared")
    materialize_codex_adapter(repo)


def materialize_project_claude(repo: Path, departments: list[str]) -> None:
    project_name = repo.name
    materialize_prepared_project(repo)
    claude_dir = repo / ".claude"
    hooks_dir = claude_dir / "hooks"
    departments_dir = claude_dir / "departments"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    departments_dir.mkdir(parents=True, exist_ok=True)

    write_project_claude_md(repo, activation_mode="activated")

    settings_template = load_template(
        TEMPLATE_ROOT,
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
        hook_template = load_template(TEMPLATE_ROOT, f"hooks/{hook_name}", fallback)
        (hooks_dir / hook_name).write_text(render_template(hook_template, project_name))

    department_template = load_template(
        TEMPLATE_ROOT,
        "departments/architecture.md",
        "# [DEPARTMENT_NAME]\n\n## Goal\nPending definition.\n",
    )
    for department in departments:
        specific_template = load_template(
            TEMPLATE_ROOT,
            f"departments/{department}.md",
            department_template,
        )
        (departments_dir / f"{department}.md").write_text(
            render_template(specific_template, project_name, department)
        )


if __name__ == "__main__":
    raise SystemExit("Use materialize_project_claude() from activation workflows.")
