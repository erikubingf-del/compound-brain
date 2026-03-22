from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_architecture_evaluator(path: Path) -> dict[str, object]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current = line[3:].strip().lower()
            sections[current] = []
            continue
        if current:
            sections[current].append(raw_line.rstrip())

    def parse_list(name: str) -> list[str]:
        values: list[str] = []
        for line in sections.get(name, []):
            stripped = line.strip()
            if stripped.startswith("- "):
                values.append(stripped[2:].strip())
        return values

    return {
        "protected_invariants": parse_list("protected invariants"),
        "deterministic_gates": parse_list("deterministic gates"),
        "architecture_rubric": parse_list("architecture rubric"),
        "keep_thresholds": parse_list("keep thresholds"),
    }


def write_architecture_scorecard(path: Path, payload: dict[str, object]) -> None:
    data = dict(payload)
    data["updated_at"] = now_utc()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


STATUS_ORDER = {
    "pending": 0,
    "fail": 1,
    "regressed": 1,
    "neutral": 2,
    "pass": 3,
    "better": 4,
}


def aggregate_status(values: list[bool]) -> str:
    return "pass" if values and all(values) else "fail"


def rubric_status(values: dict[str, str]) -> str:
    return "pass" if values and all(value == "pass" for value in values.values()) else "fail"


def has_regression(current: dict[str, str], baseline: dict[str, str]) -> bool:
    for key, current_value in current.items():
        baseline_value = baseline.get(key, "pending")
        if STATUS_ORDER.get(current_value, 0) < STATUS_ORDER.get(baseline_value, 0):
            return True
    return False


def build_architecture_scorecard(
    previous: dict[str, Any],
    deterministic_gate_results: dict[str, bool],
    rubric_results: dict[str, str],
    canary_behavior: str,
) -> dict[str, Any]:
    current = {
        "deterministic_gates": aggregate_status(list(deterministic_gate_results.values())),
        "architecture_rubric": rubric_status(rubric_results),
        "canary_behavior": canary_behavior,
    }
    baseline = dict(previous.get("baseline", {}))
    if not baseline or all(str(value) == "pending" for value in baseline.values()):
        baseline = dict(current)

    previous_rubric = dict(previous.get("details", {}).get("architecture_rubric", {}))
    decision = "keep"
    if current["deterministic_gates"] != "pass":
        decision = "discard"
    elif has_regression(rubric_results, previous_rubric):
        decision = "discard"
    elif current["canary_behavior"] not in {"neutral", "pass", "better"}:
        decision = "discard"

    return {
        "baseline": baseline,
        "current": current,
        "details": {
            "deterministic_gates": deterministic_gate_results,
            "architecture_rubric": rubric_results,
        },
        "decision": decision,
    }
