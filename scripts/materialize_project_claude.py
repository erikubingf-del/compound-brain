#!/usr/bin/env python3
"""Generate repo-local Claude control surfaces for an activated project."""

from __future__ import annotations

from pathlib import Path
import re

try:
    from scripts.lib.department_state import initialize_department_state
except ModuleNotFoundError:
    from lib.department_state import initialize_department_state


TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates" / "project_claude"
CODEX_TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "templates" / "project_codex"
MANAGED_BLOCK_START = "<!-- compound-brain managed block:begin -->"
MANAGED_BLOCK_END = "<!-- compound-brain managed block:end -->"


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


def merge_managed_block(existing: str, managed: str) -> str:
    managed_block = f"{MANAGED_BLOCK_START}\n{managed.strip()}\n{MANAGED_BLOCK_END}"
    pattern = re.compile(
        rf"{re.escape(MANAGED_BLOCK_START)}.*?{re.escape(MANAGED_BLOCK_END)}\n*",
        re.DOTALL,
    )
    if pattern.search(existing):
        return pattern.sub(managed_block + "\n\n", existing, count=1).strip() + "\n"
    if not existing.strip():
        return managed_block + "\n"
    return managed_block + "\n\n" + existing.lstrip()


def replace_section(content: str, heading: str, lines: list[str]) -> str:
    body = "\n".join(lines).rstrip() + "\n"
    pattern = re.compile(rf"(## {re.escape(heading)}\n)(.*?)(?=\n## |\Z)", re.DOTALL)
    if pattern.search(content):
        return pattern.sub(rf"\1{body}", content, count=1)
    return content.rstrip() + f"\n\n## {heading}\n{body}"


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
    claude_path = repo / "CLAUDE.md"
    existing = claude_path.read_text() if claude_path.exists() else ""
    claude_path.write_text(merge_managed_block(existing, content))


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


def materialize_autoresearch_placeholder(repo: Path) -> None:
    autoresearch_dir = repo / ".brain" / "autoresearch"
    autoresearch_dir.mkdir(parents=True, exist_ok=True)
    program_template = load_template(
        TEMPLATE_ROOT,
        "autoresearch/program.md",
        "# Program\n\n## Objective\nDefine the autoresearch objective.\n",
    )
    program_path = autoresearch_dir / "program.md"
    if not program_path.exists():
        program_path.write_text(render_template(program_template, repo.name))
    queue_path = autoresearch_dir / "queue.md"
    if not queue_path.exists():
        queue_path.write_text("# Autoresearch Queue\n\n- Define the first hypothesis.\n")
    results_path = autoresearch_dir / "results.jsonl"
    if not results_path.exists():
        results_path.write_text("")


def materialize_project_claude(
    repo: Path,
    departments: list[str],
    department_surfaces: dict[str, list[str]] | None = None,
    department_goals: dict[str, str] | None = None,
) -> None:
    project_name = repo.name
    materialize_prepared_project(repo)
    materialize_autoresearch_placeholder(repo)
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
        "# [DEPARTMENT_NAME]\n\n## Mission\nProtect the department lane.\n\n## Department Goal\nPending strategic confirmation.\n",
    )
    for department in departments:
        specific_template = load_template(
            TEMPLATE_ROOT,
            f"departments/{department}.md",
            (
                f"# [DEPARTMENT_NAME]\n\n"
                f"**Project:** [PROJECT_NAME]\n\n"
                f"## Mission\nImprove the project through the [DEPARTMENT_NAME] lane.\n\n"
                f"## Department Goal\nPending strategic confirmation.\n\n"
                f"## Owned Surfaces\n- Pending repo profile analysis.\n\n"
                f"## Protected Surfaces\n- Strategic goals without confirmation\n\n"
                f"## Allowed Actions\n- Propose bounded improvements\n\n"
                f"## Required Inputs\n- Project goal\n- Approval state\n\n"
                f"## Evaluator And Gates\n- Must stay within confirmed repo scope\n\n"
                f"## Stop Conditions\n- Strategic approval pending\n\n"
                f"## Escalation Rules\n- Escalate major scope changes\n"
            ),
        )
        content = render_template(specific_template, project_name, department)
        surfaces = list((department_surfaces or {}).get(department, []))
        goal = (department_goals or {}).get(department)
        if goal:
            content = replace_section(content, "Department Goal", [goal])
        if surfaces:
            content = replace_section(
                content,
                "Owned Surfaces",
                [f"- `{surface}`" for surface in surfaces],
            )
        (departments_dir / f"{department}.md").write_text(content)

    initialize_department_state(repo, departments)


if __name__ == "__main__":
    raise SystemExit("Use materialize_project_claude() from activation workflows.")
