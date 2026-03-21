from __future__ import annotations

from pathlib import Path
import re


def slugify(value: str) -> str:
    lowered = value.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return cleaned or "skill"


def promote_skill_pattern(
    repo: Path,
    skill_name: str,
    related_projects: list[str],
    key_knowledge: str,
    next_improvements: str,
    pattern_body: str,
) -> None:
    skills_dir = repo / ".brain" / "knowledge" / "skills"
    patterns_dir = skills_dir / "patterns"
    patterns_dir.mkdir(parents=True, exist_ok=True)

    graph_path = skills_dir / "skill-graph.md"
    if not graph_path.exists():
        graph_path.write_text("# Skill Graph\n")

    slug = slugify(skill_name)
    pattern_path = patterns_dir / f"{slug}.md"
    if not pattern_path.exists():
        pattern_path.write_text(pattern_body)

    current = graph_path.read_text()
    if skill_name not in current:
        entry = (
            f"\n## {skill_name}\n"
            f"**Level:** Intermediate\n"
            f"**Related Projects:** {', '.join(related_projects)}\n"
            f"**Key Knowledge:** {key_knowledge}\n"
            f"**Next Improvements:** {next_improvements}\n"
        )
        graph_path.write_text(current.rstrip() + "\n" + entry)
