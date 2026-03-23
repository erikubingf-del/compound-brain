from __future__ import annotations

from pathlib import Path


BEGIN_MARKER = "<!-- compound-brain:begin -->"
END_MARKER = "<!-- compound-brain:end -->"


def managed_block(claude_home: Path) -> str:
    return "\n".join(
        [
            BEGIN_MARKER,
            "# compound-brain managed runtime",
            "",
            "Use the shared compound-brain control plane.",
            "",
            "Session start protocol:",
            "- Read `~/.claude/BRAIN.md`.",
            "- Run `python3 ~/.claude/scripts/activate_repo.py --project-dir . --check-only` in repos.",
            "- If the repo is activated, run `python3 ~/.claude/scripts/codex_runtime_bridge.py --project-dir . --json-output`.",
            "- If the repo is prepared or activated, read `CLAUDE.md`, `.brain/`, and `.claude/` when present.",
            "- After the bridge runs, read `.brain/state/operator-recommendation.json`, `.brain/state/runtime-packet.json`, `.brain/state/skills.json`, and department shopping files when relevant.",
            "- Do not create a parallel repo memory or runtime outside `.brain/` and `.claude/`.",
            "",
            "Shared runtime surfaces:",
            f"- Global brain: `{claude_home}/BRAIN.md`",
            f"- Shared scripts: `{claude_home}/scripts/`",
            f"- Shared knowledge: `{claude_home}/knowledge/`",
            END_MARKER,
            "",
        ]
    )


def apply_managed_codex_block(agents_path: Path, claude_home: Path) -> None:
    agents_path.parent.mkdir(parents=True, exist_ok=True)
    block = managed_block(claude_home)
    if not agents_path.exists():
        agents_path.write_text(block)
        return

    content = agents_path.read_text()
    if BEGIN_MARKER in content and END_MARKER in content:
        start = content.index(BEGIN_MARKER)
        end = content.index(END_MARKER) + len(END_MARKER)
        updated = content[:start] + block.rstrip() + content[end:]
        agents_path.write_text(updated.strip() + "\n")
        return

    agents_path.write_text(content.rstrip() + "\n\n" + block)
