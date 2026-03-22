from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class PromotionInbox:
    root: Path

    def submit_candidate(
        self,
        source_repo: str,
        title: str,
        summary: str,
        target_kind: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.root.mkdir(parents=True, exist_ok=True)
        inbox_path = self.root / "inbox.md"
        record_id = f"{source_repo}-{target_kind}-{int(datetime.now(timezone.utc).timestamp())}"
        record = {
            "id": record_id,
            "source_repo": source_repo,
            "title": title,
            "summary": summary,
            "target_kind": target_kind,
            "status": "pending-review",
            "created_at": now_utc(),
        }
        if details:
            record.update(details)
        (self.root / f"{record_id}.json").write_text(json.dumps(record, indent=2) + "\n")

        lines = []
        if inbox_path.exists():
            lines.append(inbox_path.read_text().rstrip())
        else:
            lines.append("# Promotion Inbox")
        lines.append(
            f"- [{record_id}] {title} ({target_kind}) from `{source_repo}` — {summary}"
        )
        inbox_path.write_text("\n".join(line for line in lines if line) + "\n")
        return record
