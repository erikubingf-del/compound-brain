from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path


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

