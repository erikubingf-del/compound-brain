#!/usr/bin/env python3
"""Rank GitHub architecture findings by usefulness to compound-brain."""

from __future__ import annotations

import json
from pathlib import Path


def rank_findings(findings: list[dict]) -> list[dict]:
    ranked = []
    for finding in findings:
        row = dict(finding)
        row["score"] = round(
            float(row.get("goal_fit", 0))
            * float(row.get("architecture_fit", 0))
            * float(row.get("confidence", 0)),
            3,
        )
        ranked.append(row)
    return sorted(ranked, key=lambda row: row["score"], reverse=True)


def keyword_bonus(text: str, keywords: list[str], weight: int) -> int:
    lowered = text.lower()
    return sum(weight for keyword in keywords if keyword in lowered)


def finding_from_repo(search_term: str, repo: dict) -> dict:
    description = repo.get("description") or ""
    title = repo.get("full_name") or repo.get("name") or "unknown"
    stars = int(repo.get("stargazers_count", 0))
    goal_fit = min(
        10,
        3
        + keyword_bonus(search_term, ["agent", "hook", "knowledge", "automation", "architecture"], 1)
        + keyword_bonus(description, ["agent", "workflow", "orchestrator", "automation"], 1),
    )
    architecture_fit = min(
        10,
        3
        + keyword_bonus(description, ["architecture", "framework", "orchestrator", "workflow", "cli"], 1)
        + (2 if stars > 5000 else 1 if stars > 500 else 0),
    )
    confidence = min(0.95, 0.3 + (stars / 50000) + (0.1 if description else 0))
    return {
        "title": title,
        "url": repo.get("html_url", ""),
        "summary": description or "No description",
        "search_term": search_term,
        "goal_fit": goal_fit,
        "architecture_fit": architecture_fit,
        "confidence": round(confidence, 3),
    }


def render_radar(title: str, findings: list[dict]) -> str:
    lines = [f"# {title}", ""]
    for finding in findings:
        lines.append(f"## {finding['title']}")
        lines.append(f"- Score: {finding['score']}")
        lines.append(f"- Goal fit: {finding['goal_fit']}/10")
        lines.append(f"- Architecture fit: {finding['architecture_fit']}/10")
        lines.append(f"- Confidence: {finding['confidence']}")
        lines.append(f"- Search term: `{finding['search_term']}`")
        lines.append(f"- URL: {finding['url']}")
        lines.append(f"- Summary: {finding['summary']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Rank architecture findings from a JSON file.")
    parser.add_argument("input", help="Path to JSON file containing architecture findings")
    args = parser.parse_args()

    input_path = Path(args.input)
    findings = json.loads(input_path.read_text())
    print(json.dumps(rank_findings(findings), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
