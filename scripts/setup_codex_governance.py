#!/usr/bin/env python3
"""Install portable Project Brain governance for local Codex without changing Claude/crons."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


GLOBAL_BEGIN = "<!-- compound-brain project-governance:begin -->"
GLOBAL_END = "<!-- compound-brain project-governance:end -->"
BOARD_BEGIN = "<!-- compound-brain private-board-pointer:begin -->"
BOARD_END = "<!-- compound-brain private-board-pointer:end -->"
SKILL_MARKER = "<!-- compound-brain managed portable skill -->"
BOARD_PATTERN = re.compile(r"https://chatgpt\.com/space/page_[0-9a-f]{32}/?\Z")

GLOBAL_RULES = """# Project Brain — shared governance

For substantial work, use the portable `project-brain` skill if available
at `~/.agents/skills/project-brain/SKILL.md`.
Read the current repo `AGENTS.md`, authoritative project record, accepted
decisions, approvals and regression tests before consequential changes.
Read `~/.codex/global-agent-governance.md` if present. A private Page link
does not grant Codex access: verify retrieval before claiming it was read.
Keep user goals, people, budgets and permissions separate. Never silently
replace approved decisions or invent completed actions. For material errors,
record root cause, correction, regression test and evidence.
Do not commit private Board links or user records to public Git repositories.
"""

BOARD_RULES = """# Private Global Agent Operations Board pointer

Board URL: {url}

This local file is a pointer, not a copy of the private Board or an access
credential. Read the actual Board through an authorized connected tool only
when available; otherwise state that live Board retrieval was not verified.
For work in Codex Cloud, this local file is not automatically available.
"""


def managed_block(existing: str, begin: str, end: str, body: str) -> str:
    block = f"{begin}\n{body.strip()}\n{end}"
    if (begin in existing) != (end in existing):
        raise ValueError("Incomplete managed block: refusing to overwrite existing instructions")
    if begin in existing:
        pattern = re.compile(rf"{re.escape(begin)}.*?{re.escape(end)}", re.DOTALL)
        if len(pattern.findall(existing)) != 1:
            raise ValueError("Duplicate managed blocks: refusing to overwrite")
        return pattern.sub(lambda _: block, existing).rstrip() + "\n"
    if not existing.strip():
        return block + "\n"
    return existing.rstrip() + "\n\n" + block + "\n"


def install(
    *,
    source_skill: Path,
    codex_home: Path,
    skills_home: Path,
    board_url: str | None = None,
    check_only: bool = False,
) -> dict[str, str | bool]:
    if board_url and not BOARD_PATTERN.fullmatch(board_url):
        raise ValueError("Expected a private https://chatgpt.com/space/page_<id> URL")
    if not source_skill.is_file():
        raise FileNotFoundError(f"Portable skill source missing: {source_skill}")

    global_path = codex_home / "AGENTS.md"
    skill_path = skills_home / "project-brain" / "SKILL.md"
    board_path = codex_home / "global-agent-governance.md"

    skill_source = source_skill.read_text()
    if SKILL_MARKER not in skill_source:
        raise ValueError("Skill source is not marked as compound-brain managed")

    existing_global = global_path.read_text() if global_path.exists() else ""
    new_global = managed_block(existing_global, GLOBAL_BEGIN, GLOBAL_END, GLOBAL_RULES)
    existing_skill = skill_path.read_text() if skill_path.exists() else None
    preserve_custom_skill = existing_skill is not None and SKILL_MARKER not in existing_skill

    existing_board = board_path.read_text() if board_path.exists() else ""
    new_board = (
        managed_block(
            existing_board, BOARD_BEGIN, BOARD_END,
            BOARD_RULES.format(url=board_url.rstrip("/")),
        )
        if board_url else existing_board
    )

    if not check_only:
        global_path.parent.mkdir(parents=True, exist_ok=True)
        if new_global != existing_global:
            global_path.write_text(new_global)
        if not preserve_custom_skill and existing_skill != skill_source:
            skill_path.parent.mkdir(parents=True, exist_ok=True)
            skill_path.write_text(skill_source)
        if board_url and new_board != existing_board:
            board_path.parent.mkdir(parents=True, exist_ok=True)
            board_path.write_text(new_board)
            board_path.chmod(0o600)

    return {
        "mode": "check" if check_only else "install",
        "global_instructions": (
            "configured" if GLOBAL_BEGIN in (existing_global if check_only else new_global)
            else "missing"
        ),
        "project_brain_skill": (
            "preserved-custom" if preserve_custom_skill
            else "configured" if (existing_skill == skill_source if check_only else True)
            else "missing-or-outdated"
        ),
        "private_board_pointer": (
            "configured" if BOARD_BEGIN in (existing_board if check_only else new_board)
            else "not-configured"
        ),
        "live_private_board_retrieval": "NOT VERIFIED: requires authorized Codex connector/MCP",
        "cloud_scope": "Repo-local AGENTS.md and .agents/skills work when checked out; user-home files do not auto-sync",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Set up local Codex Project Brain skill and optional private Board pointer."
    )
    parser.add_argument("--board-url", help="Private ChatGPT Global Board Page URL")
    parser.add_argument("--check", action="store_true", help="Report status without writing")
    parser.add_argument("--codex-home", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--skills-home", type=Path, default=Path.home() / ".agents" / "skills")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "project-brain" / "SKILL.md"
    result = install(
        source_skill=source,
        codex_home=args.codex_home.expanduser(),
        skills_home=args.skills_home.expanduser(),
        board_url=args.board_url,
        check_only=args.check,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
