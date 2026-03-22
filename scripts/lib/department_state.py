from __future__ import annotations

import json
from pathlib import Path


def initialize_department_state(repo: Path, departments: list[str]) -> None:
    state_dir = repo / ".brain" / "state" / "departments"
    knowledge_dir = repo / ".brain" / "knowledge" / "departments"
    state_dir.mkdir(parents=True, exist_ok=True)
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    for department in departments:
        state_path = state_dir / f"{department}.json"
        if not state_path.exists():
            payload = {
                "department": department,
                "status": "idle",
                "approval_state": "pending",
                "current_action": "",
                "active_hypothesis": "",
                "confidence_score": 0.0,
                "last_outcome": "not-run",
            }
            state_path.write_text(json.dumps(payload, indent=2) + "\n")

        knowledge_path = knowledge_dir / f"{department}.md"
        if not knowledge_path.exists():
            knowledge_path.write_text(
                f"# {department.title()} Department Memory\n\n"
                "## Durable Lessons\n"
                "- Pending activation history.\n\n"
                "## Reusable Patterns\n"
                "- None yet.\n\n"
                "## Current Risks\n"
                "- Department goals not confirmed yet.\n\n"
                "## Recent Failure Classes\n"
                "- None yet.\n"
            )

        sources_path = knowledge_dir / f"{department}-sources.md"
        if not sources_path.exists():
            sources_path.write_text(
                f"# {department.title()} Department Sources\n\n"
                "## Objective\n"
                f"- Improve the project through the `{department}` department.\n\n"
                "## Approved Sources\n"
                "- Pending approved sources.\n\n"
                "## Search Queries\n"
                "- Pending search patterns.\n\n"
                "## Validation Policy\n"
                "- Validate external ideas against repo goals, allowed surfaces, and local checks.\n\n"
                "## Anti-goals\n"
                "- Do not adopt patterns that bypass project approvals or protected surfaces.\n"
            )

        shopping_path = state_dir / f"{department}-shopping.json"
        if not shopping_path.exists():
            shopping_path.write_text(
                json.dumps(
                    {
                        "department": department,
                        "missing_capabilities": [],
                        "candidate_skills": [],
                        "adopted_skills": [],
                        "rejected_candidates": [],
                        "next_review_at": None,
                    },
                    indent=2,
                )
                + "\n"
            )
