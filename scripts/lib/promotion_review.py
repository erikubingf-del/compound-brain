from __future__ import annotations

from datetime import date
import json
from pathlib import Path
from typing import Any


def load_candidate(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def save_candidate(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def review_pending_candidates(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    reviews_dir = root / "reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)

    pending_files = sorted(
        path for path in root.glob("*.json") if load_candidate(path).get("status") == "pending-review"
    )
    review_lines = [f"# Promotion Review — {date.today().isoformat()}", ""]
    reviewed_count = 0

    for path in pending_files:
        payload = load_candidate(path)
        payload["status"] = "review-generated"
        payload["reviewed_on"] = date.today().isoformat()
        save_candidate(path, payload)
        review_lines.append(
            f"- `{payload['id']}` [{payload['target_kind']}] from `{payload['source_repo']}`: "
            f"{payload['title']} — {payload['summary']}"
        )
        reviewed_count += 1

    review_path = reviews_dir / f"{date.today().isoformat()}.md"
    review_path.write_text("\n".join(review_lines) + "\n")
    return {"reviewed_count": reviewed_count, "review_path": str(review_path)}
