"""
agent_registry.py — Evolving per-project session continuity log.

Starts minimal (4 columns). Schema grows naturally as the project demands it.
Claude can add columns during a session; this module detects the live schema
and appends in the right format next time.

Default schema:  | Agent ID | Task Summary | Timestamp | Status |
Possible growth: | Agent ID | Role | Task Summary | Timestamp | Status |
                 | Agent ID | Role | Dept | Task Summary | Timestamp | Status |
                 ... (whatever the project earns)

Rules:
- Always auto-increments Agent ID from existing rows
- Always marks the previous active entry as idle on session start
- Always appends a new active entry
- Never breaks existing column count — unknown columns get empty values
- Never enforces a fixed schema — reads whatever is there
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REGISTRY_FILENAME = "agent-registry.md"
REGISTRY_DIR = ".brain/state"
MINIMAL_HEADER = "| Agent ID | Task Summary | Timestamp | Status |"
MINIMAL_SEPARATOR = "|----------|--------------|-----------|--------|"
REQUIRED_COLUMNS = {"agent id", "timestamp", "status"}  # always present


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _last_git_commit(repo: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            capture_output=True, text=True, check=False, cwd=str(repo),
        )
        msg = result.stdout.strip()
        return msg[:80] if msg else ""
    except Exception:
        return ""


def _action_queue_hint(repo: Path) -> str:
    queue = repo / ".brain" / "state" / "action-queue.md"
    if not queue.exists():
        return ""
    for line in queue.read_text(errors="ignore").splitlines():
        stripped = line.strip().lstrip("-").strip()
        if stripped and not stripped.startswith("#"):
            return stripped[:80]
    return ""


def _task_hint(repo: Path) -> str:
    """Pull a task hint from action-queue or last git commit."""
    hint = _action_queue_hint(repo)
    if hint:
        return hint
    return _last_git_commit(repo)


# ── Schema detection ──────────────────────────────────────────────────────────

def _parse_header(line: str) -> list[str]:
    """Parse markdown table header into column names (lowercased)."""
    parts = [p.strip().lower() for p in line.strip().strip("|").split("|")]
    return [p for p in parts if p]


def _parse_row(line: str) -> list[str]:
    """Parse markdown table row into cell values."""
    parts = [p.strip() for p in line.strip().strip("|").split("|")]
    return parts


def _format_row(values: list[str]) -> str:
    return "| " + " | ".join(values) + " |"


def _is_separator(line: str) -> bool:
    return bool(re.match(r"^\|[-| :]+\|$", line.strip()))


# ── Core operations ───────────────────────────────────────────────────────────

def _read_registry(path: Path) -> tuple[list[str], list[str]]:
    """Return (header_cols, raw_lines). Empty if file doesn't exist."""
    if not path.exists():
        return [], []
    lines = path.read_text(errors="ignore").splitlines()
    header_cols: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and not _is_separator(stripped):
            header_cols = _parse_header(stripped)
            break
    return header_cols, lines


def _next_agent_id(lines: list[str], header_cols: list[str]) -> int:
    """Find the highest Agent ID in the table and return +1."""
    if not header_cols:
        return 1
    try:
        id_idx = header_cols.index("agent id")
    except ValueError:
        return 1

    max_id = 0
    past_header = False
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if _is_separator(stripped):
            past_header = True
            continue
        if not past_header:
            continue
        cells = _parse_row(stripped)
        if len(cells) > id_idx:
            raw = cells[id_idx]
            m = re.search(r"\d+", raw)
            if m:
                max_id = max(max_id, int(m.group()))
    return max_id + 1


def _mark_active_idle(lines: list[str], header_cols: list[str]) -> tuple[list[str], str]:
    """Replace 'active' in Status column with 'idle'. Return (new_lines, last_task_summary)."""
    if not header_cols:
        return lines, ""
    try:
        status_idx = header_cols.index("status")
    except ValueError:
        return lines, ""

    task_idx: int | None = None
    for candidate in ("task summary", "current task", "task"):
        if candidate in header_cols:
            task_idx = header_cols.index(candidate)
            break

    last_task = ""
    new_lines: list[str] = []
    past_header = False

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            new_lines.append(line)
            continue
        if _is_separator(stripped):
            past_header = True
            new_lines.append(line)
            continue
        if not past_header:
            new_lines.append(line)
            continue

        cells = _parse_row(stripped)
        if len(cells) > status_idx and cells[status_idx].lower() == "active":
            cells[status_idx] = "idle"
            if task_idx is not None and len(cells) > task_idx:
                last_task = cells[task_idx]
            new_lines.append(_format_row(cells))
        else:
            new_lines.append(line)

    return new_lines, last_task


def _build_new_row(agent_id: int, header_cols: list[str], task_hint: str) -> str:
    """Build a new active row matching the current schema."""
    row: dict[str, str] = {}
    for col in header_cols:
        if col == "agent id":
            row[col] = f"Agent-{agent_id}"
        elif col in ("task summary", "current task", "task"):
            row[col] = task_hint or "—"
        elif col == "timestamp":
            row[col] = _now_utc()
        elif col == "status":
            row[col] = "active"
        else:
            row[col] = "—"
    return _format_row([row.get(col, "—") for col in header_cols])


# ── Public API ────────────────────────────────────────────────────────────────

def register_session(repo: Path) -> dict[str, str | int]:
    """
    Register a new session in the agent registry.
    Creates the registry if it doesn't exist (minimal schema).
    Returns info about the new agent entry.
    """
    registry_path = repo / REGISTRY_DIR / REGISTRY_FILENAME

    header_cols, lines = _read_registry(registry_path)

    # Bootstrap minimal schema if file is missing or empty
    if not header_cols:
        lines = [
            "# Active Agents",
            "",
            MINIMAL_HEADER,
            MINIMAL_SEPARATOR,
        ]
        header_cols = _parse_header(MINIMAL_HEADER)

    # Mark previous active as idle, capture last task
    lines, last_task = _mark_active_idle(lines, header_cols)

    # Compute next Agent ID
    agent_id = _next_agent_id(lines, header_cols)

    # Build task hint from queue / git
    task_hint = _task_hint(repo)

    # Append new row
    new_row = _build_new_row(agent_id, header_cols, task_hint)
    lines.append(new_row)

    # Write back
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text("\n".join(lines) + "\n")

    return {
        "agent_id": agent_id,
        "last_task": last_task,
        "task_hint": task_hint,
        "registry_path": str(registry_path.relative_to(repo)),
    }
