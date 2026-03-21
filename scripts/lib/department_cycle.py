from __future__ import annotations

from datetime import date, datetime, timezone
import json
from pathlib import Path
from typing import Any


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def choose_bounded_action(repo: Path, department: str) -> str:
    queue_path = repo / ".brain" / "state" / "action-queue.md"
    if queue_path.exists():
        for line in queue_path.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                return stripped[2:]
    return f"Review {department} backlog"


def persist_department_state(
    repo: Path,
    department: str,
    status: str,
    reason: str,
    action: str,
) -> None:
    state_path = repo / ".brain" / "state" / "departments" / f"{department}.json"
    payload = load_json(
        state_path,
        {
            "department": department,
            "status": "idle",
            "approval_state": "pending",
            "current_action": "",
            "active_hypothesis": "",
            "confidence_score": 0.0,
            "last_outcome": "not-run",
        },
    )
    payload["status"] = status
    payload["current_action"] = action
    payload["last_outcome"] = reason
    payload["last_run"] = now_utc()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2) + "\n")


def append_daily_summary(repo: Path, department: str, result: dict[str, Any]) -> None:
    daily_dir = repo / ".brain" / "knowledge" / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    daily_path = daily_dir / f"{date.today().isoformat()}.md"
    if not daily_path.exists():
        daily_path.write_text(f"# {date.today().isoformat()} — {repo.name}\n\n## Session Notes\n")
    with daily_path.open("a") as handle:
        handle.write(
            f"- Department `{department}` -> {result['status']} ({result['reason']})"
            f": {result['action']}\n"
        )


def run_department_cycle(repo: Path, department: str) -> dict[str, Any]:
    repo = repo.resolve()
    approval = load_json(
        repo / ".brain" / "state" / "approval-state.json",
        {"state": "inactive", "pending": []},
    )
    action = choose_bounded_action(repo, department)
    if approval.get("pending"):
        result = {
            "department": department,
            "status": "blocked",
            "reason": "approval-pending",
            "action": action,
        }
        persist_department_state(repo, department, "blocked", "approval-pending", action)
        append_daily_summary(repo, department, result)
        return result

    result = {
        "department": department,
        "status": "ready",
        "reason": "bounded-action-queued",
        "action": action,
    }
    persist_department_state(repo, department, "ready", "bounded-action-queued", action)
    append_daily_summary(repo, department, result)
    return result
