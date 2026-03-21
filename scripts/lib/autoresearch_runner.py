from __future__ import annotations

from datetime import datetime, timezone
import json
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts.lib.autoresearch_program import load_autoresearch_program
except ModuleNotFoundError:
    from lib.autoresearch_program import load_autoresearch_program


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def current_commit(repo: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(repo),
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def first_hypothesis(queue_path: Path) -> str:
    if not queue_path.exists():
        return "Define the first experiment hypothesis"
    for line in queue_path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            return stripped[2:]
    return "Define the first experiment hypothesis"


def run_autoresearch_cycle(repo: Path, department: str) -> dict[str, Any]:
    repo = repo.resolve()
    approval = load_json(
        repo / ".brain" / "state" / "approval-state.json",
        {"state": "inactive", "pending": []},
    )
    if "autoresearch_enable" in approval.get("pending", []):
        return {
            "department": department,
            "status": "blocked",
            "reason": "autoresearch-not-approved",
        }

    autoresearch_dir = repo / ".brain" / "autoresearch"
    program_path = autoresearch_dir / "program.md"
    if not program_path.exists():
        return {
            "department": department,
            "status": "blocked",
            "reason": "missing-program",
        }

    program = load_autoresearch_program(program_path)
    baseline_path = autoresearch_dir / "baseline.json"
    if not baseline_path.exists():
        baseline = {
            "baseline_commit": current_commit(repo),
            "baseline_metric": "pending",
            "timestamp": now_utc(),
            "evaluator_version": program.get("fixed_evaluator", ""),
        }
        baseline_path.write_text(json.dumps(baseline, indent=2) + "\n")

    hypothesis = first_hypothesis(autoresearch_dir / "queue.md")
    result = {
        "timestamp": now_utc(),
        "department": department,
        "status": "queued",
        "reason": "awaiting-evaluator-execution",
        "hypothesis": hypothesis,
        "objective": program.get("objective", ""),
        "commit": current_commit(repo),
    }
    with (autoresearch_dir / "results.jsonl").open("a") as handle:
        handle.write(json.dumps(result) + "\n")
    return result
