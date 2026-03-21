#!/usr/bin/env python3
"""
project_intelligence.py — Universal per-project LLM intelligence briefing.

Works for ANY project that has CLAUDE.md or .brain/.
Collects local state → calls claude CLI → writes brief to .brain/daily/.

Usage:
    python3 project_intelligence.py --project-dir /path/to/project
    python3 project_intelligence.py --project-dir /path/to/project --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CLAUDE_BIN = "__CLAUDE_BIN__"
GLOBAL_KNOWLEDGE = Path.home() / ".claude" / "knowledge"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def date_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def read_safe(path: Path, max_chars: int = 2000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""


# ─── Collectors ─────────────────────────────────────────────────────────────

def get_git_activity(project_dir: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-15", "--no-decorate"],
            capture_output=True, text=True, timeout=10, cwd=str(project_dir)
        )
        return result.stdout.strip() or "No commits found"
    except Exception as e:
        return f"git log failed: {e}"


def get_git_status(project_dir: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True, timeout=5, cwd=str(project_dir)
        )
        out = result.stdout.strip()
        return out if out else "Clean working tree"
    except Exception as e:
        return f"git status failed: {e}"


def get_project_claude_md(project_dir: Path) -> str:
    """Extract the first 80 lines of CLAUDE.md (project identity section)."""
    path = project_dir / "CLAUDE.md"
    content = read_safe(path, max_chars=3000)
    lines = content.split("\n")[:80]
    return "\n".join(lines)


def get_brain_memory(project_dir: Path) -> dict[str, str]:
    """Read .brain/memory/ files for project context."""
    brain_mem = project_dir / ".brain" / "memory"
    result: dict[str, str] = {}
    if not brain_mem.exists():
        return result
    for f in sorted(brain_mem.glob("*.md"))[:6]:
        content = read_safe(f, max_chars=800)
        if content:
            result[f.name] = content
    return result


def get_planning_state(project_dir: Path) -> str:
    """Read .planning/STATE.md if it exists."""
    for candidate in [
        project_dir / ".planning" / "STATE.md",
        project_dir / ".planning" / "ROADMAP.md",
    ]:
        content = read_safe(candidate, max_chars=1200)
        if content:
            return f"[{candidate.name}]\n{content}"
    return "No planning files found"


def get_brain_daily_errors(project_dir: Path) -> str:
    """Get today's errors from .brain daily note."""
    d = date_str()
    path = project_dir / ".brain" / "knowledge" / "daily" / f"{d}.md"
    content = read_safe(path, max_chars=3000)
    if not content:
        return "No daily log today"
    lines = content.split("\n")
    errors = [l for l in lines if any(kw in l for kw in ["Error in:", "FAILED", "KeyError", "Exception:", "Traceback"])]
    deploys_ok = sum(1 for l in lines if "[SUCCESS]" in l)
    deploys_fail = sum(1 for l in lines if "[FAILED]" in l)
    summary = f"Today: {len(errors)} errors, {deploys_ok} deploys OK, {deploys_fail} deploys failed"
    if errors:
        summary += "\nSample: " + " | ".join(e.strip()[:60] for e in errors[:4])
    return summary


def get_file_tree(project_dir: Path) -> str:
    """Top-level file listing for project structure context."""
    try:
        items = sorted(project_dir.iterdir())
        names = [
            f.name for f in items
            if not f.name.startswith(".") and f.name not in ["node_modules", "__pycache__", "venv", ".git"]
        ][:20]
        return ", ".join(names)
    except Exception:
        return "Unable to list files"


def get_last_session_context(project_dir: Path) -> str:
    """Read .brain MEMORY.md + global project memory for recent session context."""
    results = []

    # .brain/MEMORY.md index
    mem_index = project_dir / ".brain" / "MEMORY.md"
    if mem_index.exists():
        results.append(f"[Brain Memory Index]\n{read_safe(mem_index, 500)}")

    # Global project knowledge
    global_proj = GLOBAL_KNOWLEDGE / "daily" / f"{date_str()}.md"
    if global_proj.exists():
        excerpt = read_safe(global_proj, 600)
        if excerpt:
            results.append(f"[Global daily note excerpt]\n{excerpt}")

    return "\n\n".join(results) or "No session context available"


# ─── Prompt composer ─────────────────────────────────────────────────────────

def compose_prompt(
    project_name: str,
    claude_md: str,
    git_log: str,
    git_status: str,
    brain_memory: dict[str, str],
    planning_state: str,
    daily_errors: str,
    session_context: str,
    file_tree: str,
) -> str:
    ts = now_utc()
    memory_text = ""
    if brain_memory:
        memory_text = "\n".join(f"  [{fname}]\n  {content[:300]}" for fname, content in brain_memory.items())
    else:
        memory_text = "  (no .brain/memory files yet)"

    return f"""You are an autonomous intelligence analyst for the project "{project_name}".
Generate a concise briefing and improvement plan for {ts}.

## Project Identity (CLAUDE.md excerpt)
{claude_md[:600] if claude_md else "No CLAUDE.md found"}

## Recent Git Activity
{git_log}

## Git Status
{git_status}

## Project Memory
{memory_text}

## Planning State
{planning_state}

## Today's Errors/Deployments
{daily_errors}

## Session Context
{session_context}

## Top-level Files
{file_tree}

---
Generate a structured briefing:

**STATUS** (1 line): Is this project active/healthy/stale/blocked?

**RECENT PROGRESS** (2-3 bullets): What was accomplished recently based on git log?

**TOP 3 IMPROVEMENT OPPORTUNITIES**: Specific actionable improvements for this project.
For each: what to do, why, and what file/command is involved.

**RISKS** (2 bullets): What could break or degrade if left unattended?

**NEXT SESSION ACTION**: Single most important thing to do next session (be specific).

Rules: max 300 words, bullet points, no preamble."""


# ─── Output ───────────────────────────────────────────────────────────────────

def call_claude(prompt: str) -> str:
    try:
        result = subprocess.run(
            [CLAUDE_BIN, "--dangerously-skip-permissions", "--print", "-p", prompt],
            capture_output=True, text=True, timeout=90,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return f"[claude error rc={result.returncode}]: {result.stderr[:300]}"
    except subprocess.TimeoutExpired:
        return "[claude timed out]"
    except FileNotFoundError:
        return f"[claude binary not found at {CLAUDE_BIN}]"
    except Exception as e:
        return f"[claude call failed: {e}]"


def write_brief(project_dir: Path, project_name: str, analysis: str) -> None:
    ts = now_utc()
    d = date_str()

    brain_daily = project_dir / ".brain" / "knowledge" / "daily"
    brain_daily.mkdir(parents=True, exist_ok=True)

    daily_path = brain_daily / f"{d}.md"
    latest_path = brain_daily / "intelligence_brief_latest.md"

    section = f"\n\n## AI Intelligence Brief [{ts}]\n\n{analysis}\n"

    if daily_path.exists():
        with open(daily_path, "a") as f:
            f.write(section)
    else:
        with open(daily_path, "w") as f:
            f.write(f"# Daily Log — {d} [{project_name}]{section}")

    latest_path.write_text(f"# Intelligence Brief — {project_name} [{ts}]\n\n{analysis}\n")

    print(f"  ✓ Brief written → {daily_path}")
    print(f"  ✓ Latest → {latest_path}")


# ─── Main ────────────────────────────────────────────────────────────────────

def run_for_project(project_dir: Path, dry_run: bool = False) -> str | None:
    if not project_dir.exists():
        print(f"  [skip] {project_dir} does not exist")
        return None

    project_name = project_dir.name
    print(f"[intelligence:{project_name}] Collecting...")

    claude_md = get_project_claude_md(project_dir)
    git_log = get_git_activity(project_dir)
    git_status = get_git_status(project_dir)
    brain_memory = get_brain_memory(project_dir)
    planning_state = get_planning_state(project_dir)
    daily_errors = get_brain_daily_errors(project_dir)
    session_context = get_last_session_context(project_dir)
    file_tree = get_file_tree(project_dir)

    prompt = compose_prompt(
        project_name, claude_md, git_log, git_status,
        brain_memory, planning_state, daily_errors,
        session_context, file_tree
    )

    if dry_run:
        print(f"\n{'='*60}\nPROMPT for {project_name}:\n{'='*60}\n{prompt}\n{'='*60}")
        return None

    print(f"  Calling claude ({len(prompt)} chars)...")
    analysis = call_claude(prompt)

    write_brief(project_dir, project_name, analysis)
    return analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Per-project LLM intelligence briefing")
    parser.add_argument("--project-dir", required=True, help="Path to project directory")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt, skip claude")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    print(f"[intelligence] Starting {now_utc()} — {project_dir.name}")
    run_for_project(project_dir, dry_run=args.dry_run)
    print("[intelligence] Done.")


if __name__ == "__main__":
    main()
