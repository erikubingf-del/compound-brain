from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_utc_string() -> str:
    return now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_utc(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


@dataclass
class RepoPreviewCache:
    path: Path
    cooldown_days: int = 7

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"previews": []}
        return json.loads(self.path.read_text())

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2) + "\n")

    def upsert_preview(
        self,
        repo_path: str,
        repo_name: str,
        inferred_goal: str,
        departments: list[str],
        risks: list[str],
        next_actions: list[str],
        confidence: float,
        last_commit: str,
        dismissal_state: str = "active",
    ) -> dict[str, Any]:
        data = self.load()
        now = now_utc()
        next_review_after = now + timedelta(days=self.cooldown_days)
        record = {
            "repo_path": repo_path,
            "repo_name": repo_name,
            "inferred_goal": inferred_goal,
            "departments": departments,
            "risks": risks,
            "next_actions": next_actions,
            "confidence": confidence,
            "last_commit": last_commit,
            "dismissal_state": dismissal_state,
            "updated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "next_review_after": next_review_after.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        data["previews"] = [
            preview for preview in data["previews"] if preview.get("repo_path") != repo_path
        ]
        data["previews"].append(record)
        self.save(data)
        return record

    def load_preview(self, repo_path: str) -> dict[str, Any] | None:
        data = self.load()
        for preview in data["previews"]:
            if preview.get("repo_path") == repo_path:
                return preview
        return None

    def list_due_previews(self, current_time: datetime | None = None) -> list[dict[str, Any]]:
        current = current_time or now_utc()
        due: list[dict[str, Any]] = []
        for preview in self.load()["previews"]:
            next_review = preview.get("next_review_after")
            if not next_review or parse_utc(next_review) <= current:
                due.append(preview)
        return due
