#!/usr/bin/env python3
"""Report heartbeat health for activated compound-brain repos."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.lib.runtime_heartbeat import RuntimeHeartbeatStore, classify_cron_event
except ModuleNotFoundError:
    from lib.runtime_heartbeat import RuntimeHeartbeatStore, classify_cron_event


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def claude_home_dir() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".claude"


def activation_registry_path() -> Path:
    return claude_home_dir() / "registry" / "activated-projects.json"


def load_registry() -> list[dict]:
    path = activation_registry_path()
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return list(data.get("projects", []))


def heartbeat_store() -> RuntimeHeartbeatStore:
    root = claude_home_dir() / "registry"
    return RuntimeHeartbeatStore(
        heartbeat_root=root / "runtime-heartbeats",
        lock_root=root / "runtime-locks",
    )


def write_watchdog_report(entries: list[dict]) -> dict[str, object]:
    claude_home = claude_home_dir()
    report_path = claude_home / "knowledge" / "resources" / "runtime-heartbeats.md"
    report_json = claude_home / "registry" / "runtime-heartbeats-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_json.parent.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1

    lines = [f"# Runtime Heartbeats — {now_utc()}", ""]
    lines.append("## Summary")
    for status in sorted(counts):
        lines.append(f"- {status}: {counts[status]}")
    if not counts:
        lines.append("- no activated repos")

    lines.append("")
    lines.append("## Repos")
    for entry in entries:
        detail = f"`{entry['repo_name']}` — {entry['status']}"
        if entry.get("last_success_at"):
            detail += f" | last success: {entry['last_success_at']}"
        if entry.get("next_due_at"):
            detail += f" | next due: {entry['next_due_at']}"
        if entry.get("last_error_class"):
            detail += f" | error: {entry['last_error_class']}"
        lines.append(f"- {detail}")

    report_path.write_text("\n".join(lines) + "\n")
    report_json.write_text(json.dumps({"generated_at": now_utc(), "entries": entries, "counts": counts}, indent=2) + "\n")
    return {"report_path": str(report_path), "counts": counts}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate compound-brain runtime heartbeat report.")
    parser.parse_args(argv)
    registry = load_registry()
    store = heartbeat_store()

    keyed_records = {record["repo_path"]: record for record in store.load_all()}
    entries = []
    for project in registry:
        repo_path = str(Path(project["repo_path"]).resolve())
        record = keyed_records.get(repo_path, {"repo_path": repo_path, "repo_name": project["repo_name"], "events": {}})
        cron = record.get("events", {}).get("cron", {})
        entries.append(
            {
                "repo_path": repo_path,
                "repo_name": record.get("repo_name", project["repo_name"]),
                "status": classify_cron_event(record),
                "last_success_at": cron.get("last_success_at"),
                "next_due_at": cron.get("next_due_at"),
                "last_error_class": cron.get("last_error_class"),
            }
        )

    result = write_watchdog_report(entries)
    print(f"compound-brain runtime watchdog report: {result['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
