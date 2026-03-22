from __future__ import annotations

from datetime import date
import json
import re
from pathlib import Path
from typing import Any

try:
    from scripts.lib.skill_evolution import upsert_skill_pattern
except ModuleNotFoundError:
    from lib.skill_evolution import upsert_skill_pattern


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def next_qmp_number(qmp_dir: Path) -> int:
    existing = [
        int(match.group(1))
        for path in qmp_dir.glob("qmp-*.md")
        if (match := re.search(r"qmp-(\d+)\.md$", path.name))
    ]
    return max(existing, default=0) + 1


def next_decision_number(log_path: Path) -> int:
    if not log_path.exists():
        return 1
    existing = [
        int(match.group(1))
        for match in re.finditer(r"## DEC-(\d+)\s+—", log_path.read_text())
    ]
    return max(existing, default=0) + 1


def ensure_qmp_index(index_path: Path) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if not index_path.exists():
        index_path.write_text(
            "# QMP Index\n\n| ID | Question | File |\n|----|----------|------|\n"
        )


def append_unique_line(path: Path, line: str) -> None:
    if path.exists():
        content = path.read_text()
        if line in content:
            return
        path.write_text(content.rstrip() + "\n" + line + "\n")
        return
    path.write_text(line + "\n")


def apply_skill_candidate(knowledge_root: Path, payload: dict[str, Any]) -> list[str]:
    pattern_path = upsert_skill_pattern(
        skills_dir=knowledge_root / "skills",
        skill_name=str(payload.get("skill_name") or payload["title"]),
        related_projects=[str(payload.get("source_repo", "unknown"))],
        key_knowledge=str(payload.get("key_knowledge") or payload["summary"]),
        next_improvements=str(payload.get("next_improvements") or "Review future cross-project applicability."),
        pattern_body=str(
            payload.get("pattern_body")
            or f"# {payload.get('skill_name') or payload['title']}\n\n{payload['summary']}\n"
        ),
    )
    return [
        str(knowledge_root / "skills" / "skill-graph.md"),
        str(pattern_path),
    ]


def apply_qmp_candidate(knowledge_root: Path, payload: dict[str, Any]) -> list[str]:
    qmp_dir = knowledge_root / "qmp"
    qmp_dir.mkdir(parents=True, exist_ok=True)
    ensure_qmp_index(qmp_dir / "_index.md")

    number = next_qmp_number(qmp_dir)
    qmp_id = f"QMP-{number:03d}"
    qmp_file = qmp_dir / f"qmp-{number:03d}.md"
    question = str(payload.get("question") or payload["title"])
    model = str(payload.get("model") or payload["summary"])
    process = str(payload.get("process") or "Review the candidate and adapt it into a repeatable operating process.")
    applied_to = str(payload.get("applied_to") or payload.get("source_repo", "compound-brain"))
    pitfalls = str(payload.get("pitfalls") or "Validate the pattern against fixed evaluators before broad adoption.")

    qmp_file.write_text(
        "\n".join(
            [
                f"# {qmp_id} — {question}",
                "",
                "## Q — Question",
                question,
                "",
                "## M — Model",
                model,
                "",
                "## P — Process",
                process,
                "",
                "## Applied To",
                applied_to,
                "",
                "## Pitfalls",
                pitfalls,
                "",
            ]
        )
    )
    append_unique_line(
        qmp_dir / "_index.md",
        f"| {number:03d} | {question} | [qmp-{number:03d}.md](qmp-{number:03d}.md) |",
    )
    return [str(qmp_file), str(qmp_dir / "_index.md")]


def apply_decision_candidate(knowledge_root: Path, payload: dict[str, Any]) -> list[str]:
    decisions_dir = knowledge_root / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)
    log_path = decisions_dir / "log.md"
    if not log_path.exists():
        log_path.write_text("# Decision Log\n\n---\n")

    number = next_decision_number(log_path)
    entry = "\n".join(
        [
            f"## DEC-{number:03d} — {payload.get('decision_title') or payload['title']}",
            f"**Date:** {date.today().isoformat()}",
            f"**Priority:** {payload.get('priority') or 'P2'}",
            f"**Context:** {payload.get('context') or payload['summary']}",
            "**Options Considered:**",
            *(f"- {item}" for item in payload.get("options_considered", ["Promote", "Do nothing"])),
            f"**Reasoning:** {payload.get('reasoning') or payload['summary']}",
            f"**Expected Outcome:** {payload.get('expected_outcome') or 'Improve cross-project orchestration quality.'}",
            f"**Actual Outcome:** {payload.get('actual_outcome') or 'Pending'}",
            f"**Rule established:** {payload.get('rule_established') or payload['summary']}",
            "",
            "---",
            "",
        ]
    )
    log_path.write_text(log_path.read_text().rstrip() + "\n\n" + entry)
    return [str(log_path)]


def apply_approved_candidates(promotions_root: Path, knowledge_root: Path) -> dict[str, Any]:
    promotions_root.mkdir(parents=True, exist_ok=True)
    knowledge_root.mkdir(parents=True, exist_ok=True)

    applied_count = 0
    applied_targets: list[str] = []
    for path in sorted(promotions_root.glob("*.json")):
        payload = load_json(path)
        if payload.get("status") not in {"approved", "approved-for-apply"}:
            continue

        kind = str(payload.get("target_kind", ""))
        if kind == "skills":
            targets = apply_skill_candidate(knowledge_root, payload)
        elif kind == "qmp":
            targets = apply_qmp_candidate(knowledge_root, payload)
        elif kind == "decisions":
            targets = apply_decision_candidate(knowledge_root, payload)
        else:
            payload["status"] = "unsupported-target"
            save_json(path, payload)
            continue

        payload["status"] = "applied"
        payload["applied_on"] = date.today().isoformat()
        payload["applied_targets"] = targets
        save_json(path, payload)
        applied_count += 1
        applied_targets.extend(targets)

    return {"applied_count": applied_count, "applied_targets": applied_targets}
