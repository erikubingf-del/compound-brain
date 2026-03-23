#!/usr/bin/env python3
"""Codex bridge into the shared compound-brain repo runtime."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.project_runtime_event import run_project_runtime_event
except ModuleNotFoundError:
    from project_runtime_event import run_project_runtime_event


def parse_iso8601(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def is_activated_repo(repo: Path) -> bool:
    return (repo / ".brain").exists() and (repo / ".claude" / "settings.local.json").exists()


def runtime_state_is_fresh(runtime_packet: dict[str, Any], *, max_age_seconds: int) -> bool:
    generated_at = parse_iso8601(str(runtime_packet.get("generated_at", "")))
    if generated_at is None:
        return False
    age_seconds = (datetime.now(timezone.utc) - generated_at).total_seconds()
    return age_seconds <= max_age_seconds


def ensure_codex_repo_runtime(repo: Path, max_age_seconds: int = 900) -> dict[str, Any]:
    repo = repo.resolve()
    if not is_activated_repo(repo):
        return {"status": "skipped", "reason": "repo-not-activated", "repo": repo.name}

    state_dir = repo / ".brain" / "state"
    runtime_packet_path = state_dir / "runtime-packet.json"
    recommendation_path = state_dir / "operator-recommendation.json"
    if runtime_packet_path.exists() and recommendation_path.exists():
        runtime_packet = json.loads(runtime_packet_path.read_text())
        recommendation = json.loads(recommendation_path.read_text())
        if runtime_state_is_fresh(runtime_packet, max_age_seconds=max_age_seconds):
            return {
                "status": "fresh",
                "repo": repo.name,
                "current_depth": runtime_packet.get("current_depth"),
                "recommended_next_action": recommendation.get("recommended_next_action"),
                "lead_department": recommendation.get("lead_department"),
                "new_opportunities": recommendation.get("new_opportunities", []),
            }

    result = run_project_runtime_event(repo, "session-start")
    if recommendation_path.exists():
        recommendation = json.loads(recommendation_path.read_text())
        result.setdefault("recommended_next_action", recommendation.get("recommended_next_action"))
        result.setdefault("new_opportunities", recommendation.get("new_opportunities", []))
        result.setdefault("lead_department", recommendation.get("lead_department"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Ensure Codex wakes into the shared compound-brain repo runtime.")
    parser.add_argument("--project-dir", help="Activated repo path", default=".")
    parser.add_argument("--max-age-seconds", type=int, default=900)
    parser.add_argument("--json-output", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    result = ensure_codex_repo_runtime(Path(args.project_dir), max_age_seconds=args.max_age_seconds)
    if args.json_output:
        print(json.dumps(result, sort_keys=True))
    elif os.environ.get("COMPOUND_BRAIN_RUNTIME_VERBOSE", "").lower() in {"1", "true", "yes"}:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
