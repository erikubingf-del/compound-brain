from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class ActivationRegistry:
    path: Path

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"projects": []}
        return json.loads(self.path.read_text())

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2) + "\n")

    def register_repo(
        self,
        repo_path: str,
        repo_name: str,
        stack: list[str],
        activation_mode: str,
    ) -> dict[str, Any]:
        data = self.load()
        record = {
            "repo_path": repo_path,
            "repo_name": repo_name,
            "stack": stack,
            "activation_mode": activation_mode,
            "status": "registered",
            "updated_at": now_utc(),
        }
        data["projects"] = [
            project for project in data["projects"] if project.get("repo_path") != repo_path
        ]
        data["projects"].append(record)
        self.save(data)
        return record
