from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def isoformat(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def repo_key(repo_path: Path) -> str:
    return hashlib.sha1(str(repo_path.resolve()).encode("utf-8")).hexdigest()[:12]


def default_interval_minutes(event: str) -> int | None:
    if event == "cron":
        return 360
    return None


def failure_backoff_minutes(consecutive_failures: int) -> int:
    return min(15 * (2 ** max(consecutive_failures - 1, 0)), 360)


def default_event_state() -> dict[str, Any]:
    return {
        "status": "never-run",
        "last_run_at": None,
        "last_success_at": None,
        "last_failure_at": None,
        "next_due_at": None,
        "consecutive_failures": 0,
        "last_duration_seconds": 0.0,
        "last_error_class": None,
        "last_error_message": None,
        "last_summary": None,
        "backoff_minutes": 0,
    }


@dataclass
class RuntimeHeartbeatStore:
    heartbeat_root: Path
    lock_root: Path

    def heartbeat_path(self, repo_path: Path) -> Path:
        key = repo_key(repo_path)
        repo_name = repo_path.resolve().name or "repo"
        return self.heartbeat_root / f"{repo_name}-{key}.json"

    def lock_path(self, repo_path: Path) -> Path:
        key = repo_key(repo_path)
        repo_name = repo_path.resolve().name or "repo"
        return self.lock_root / f"{repo_name}-{key}.lock"

    def load(self, repo_path: Path) -> dict[str, Any]:
        path = self.heartbeat_path(repo_path)
        if not path.exists():
            return {
                "repo_path": str(repo_path.resolve()),
                "repo_name": repo_path.resolve().name,
                "repo_key": repo_key(repo_path),
                "updated_at": None,
                "events": {},
            }
        return json.loads(path.read_text())

    def save(self, repo_path: Path, payload: dict[str, Any]) -> None:
        path = self.heartbeat_path(repo_path)
        self.heartbeat_root.mkdir(parents=True, exist_ok=True)
        payload["updated_at"] = isoformat(now_utc())
        path.write_text(json.dumps(payload, indent=2) + "\n")

    def load_all(self) -> list[dict[str, Any]]:
        self.heartbeat_root.mkdir(parents=True, exist_ok=True)
        return [json.loads(path.read_text()) for path in sorted(self.heartbeat_root.glob("*.json"))]

    def acquire_lock(self, repo_path: Path, event: str, stale_after_seconds: int = 7200) -> tuple[bool, dict[str, Any] | None]:
        self.lock_root.mkdir(parents=True, exist_ok=True)
        path = self.lock_path(repo_path)
        payload = {
            "repo_path": str(repo_path.resolve()),
            "repo_name": repo_path.resolve().name,
            "event": event,
            "acquired_at": isoformat(now_utc()),
            "pid": os.getpid(),
        }
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            fd = os.open(path, flags)
            with os.fdopen(fd, "w") as handle:
                handle.write(json.dumps(payload, indent=2) + "\n")
            return True, payload
        except FileExistsError:
            current = json.loads(path.read_text()) if path.exists() else {}
            acquired_at = parse_timestamp(current.get("acquired_at"))
            if acquired_at and (now_utc() - acquired_at).total_seconds() > stale_after_seconds:
                path.unlink(missing_ok=True)
                return self.acquire_lock(repo_path, event, stale_after_seconds=stale_after_seconds)
            return False, current

    def release_lock(self, repo_path: Path) -> None:
        self.lock_path(repo_path).unlink(missing_ok=True)

    def mark_start(self, repo_path: Path, event: str) -> dict[str, Any]:
        payload = self.load(repo_path)
        state = dict(payload.get("events", {}).get(event, default_event_state()))
        state["status"] = "running"
        state["last_run_at"] = isoformat(now_utc())
        payload.setdefault("events", {})[event] = state
        self.save(repo_path, payload)
        return payload

    def mark_success(self, repo_path: Path, event: str, duration_seconds: float, summary: str | None = None) -> dict[str, Any]:
        payload = self.load(repo_path)
        state = dict(payload.get("events", {}).get(event, default_event_state()))
        state["status"] = "ok"
        state["last_run_at"] = isoformat(now_utc())
        state["last_success_at"] = state["last_run_at"]
        state["last_duration_seconds"] = round(duration_seconds, 3)
        state["consecutive_failures"] = 0
        state["last_error_class"] = None
        state["last_error_message"] = None
        state["backoff_minutes"] = 0
        state["last_summary"] = summary
        interval = default_interval_minutes(event)
        state["next_due_at"] = (
            isoformat(now_utc() + timedelta(minutes=interval)) if interval is not None else None
        )
        payload.setdefault("events", {})[event] = state
        self.save(repo_path, payload)
        return payload

    def mark_failure(
        self,
        repo_path: Path,
        event: str,
        error_class: str,
        error_message: str,
        duration_seconds: float,
    ) -> dict[str, Any]:
        payload = self.load(repo_path)
        state = dict(payload.get("events", {}).get(event, default_event_state()))
        failures = int(state.get("consecutive_failures", 0)) + 1
        backoff = failure_backoff_minutes(failures)
        state["status"] = "failed"
        state["last_run_at"] = isoformat(now_utc())
        state["last_failure_at"] = state["last_run_at"]
        state["last_duration_seconds"] = round(duration_seconds, 3)
        state["consecutive_failures"] = failures
        state["last_error_class"] = error_class
        state["last_error_message"] = error_message[:400]
        state["backoff_minutes"] = backoff
        interval = default_interval_minutes(event)
        target_minutes = backoff if interval is not None else None
        state["next_due_at"] = (
            isoformat(now_utc() + timedelta(minutes=target_minutes)) if target_minutes is not None else None
        )
        payload.setdefault("events", {})[event] = state
        self.save(repo_path, payload)
        return payload


def classify_cron_event(record: dict[str, Any], reference_time: datetime | None = None) -> str:
    now = reference_time or now_utc()
    events = record.get("events", {})
    cron = events.get("cron")
    if not cron:
        return "missing-heartbeat"
    if cron.get("status") == "running":
        return "running"
    if cron.get("status") == "failed":
        next_due = parse_timestamp(cron.get("next_due_at"))
        if next_due and next_due > now:
            return "backoff"
        return "failing"
    next_due = parse_timestamp(cron.get("next_due_at"))
    if next_due and next_due < now:
        return "overdue"
    return "healthy"
