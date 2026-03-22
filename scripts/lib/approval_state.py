from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class ApprovalStateStore:
    state_dir: Path

    def __post_init__(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / "approval-state.json"
        self.pending_path = self.state_dir / "pending-approvals.md"

    def load(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"state": "inactive", "pending": []}
        return json.loads(self.state_path.read_text())

    def save(self, payload: dict[str, Any]) -> None:
        self.state_path.write_text(json.dumps(payload, indent=2) + "\n")

    def write_pending_markdown(self, payload: dict[str, Any]) -> None:
        lines = [
            "# Pending Approvals",
            "",
            f"**State:** {payload['state']}",
            "",
            "## Pending Items",
        ]
        for item in payload.get("pending", []):
            lines.append(f"- {item}")
        candidates = payload.get("project_goal_candidates", [])
        if candidates:
            lines.extend(["", "## Project Goal Candidates"])
            for candidate in candidates:
                lines.append(f"- {candidate}")
        department_goals = payload.get("department_goals", {})
        if department_goals:
            lines.extend(["", "## Department Goals"])
            for department, goal in department_goals.items():
                lines.append(f"- `{department}`: {goal}")
        recommendation = payload.get("recommendation")
        if isinstance(recommendation, dict) and recommendation:
            lines.extend(["", "## Recommendation"])
            if recommendation.get("message"):
                lines.append(f"- {recommendation['message']}")
            if recommendation.get("recommended_project_goal"):
                lines.append(f"- `project_goal`: {recommendation['recommended_project_goal']}")
            recommended_departments = recommendation.get("recommended_departments", [])
            if recommended_departments:
                lines.append(
                    "- `departments`: " + ", ".join(f"`{item}`" for item in recommended_departments)
                )
            lines.append("- Want me to do that?")
        self.pending_path.write_text("\n".join(lines) + "\n")

    def initialize(
        self,
        project_goal_candidates: list[str],
        departments: list[str],
        recommendation: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        # Never overwrite an already-approved state — human approval is durable.
        existing = self.load()
        if existing.get("state") == "approved":
            return existing

        payload = {
            "state": "awaiting-project-goal",
            "pending": ["project_goal", "department_goals"],
            "project_goal_candidates": project_goal_candidates,
            "department_goals": {
                department: f"Confirm goal for {department}"
                for department in departments
            },
            "updated_at": now_utc(),
        }
        if recommendation:
            payload["recommendation"] = recommendation
        self.save(payload)
        self.write_pending_markdown(payload)
        return payload

    def record_transition(
        self,
        state: str,
        reason: str,
        pending: list[str],
    ) -> dict[str, Any]:
        payload = self.load()
        payload["state"] = state
        payload["reason"] = reason
        payload["pending"] = pending
        payload["updated_at"] = now_utc()
        self.save(payload)
        self.write_pending_markdown(payload)
        return payload
