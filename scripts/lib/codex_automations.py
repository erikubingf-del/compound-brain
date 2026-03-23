from __future__ import annotations

from datetime import datetime, timezone
import json
import tomllib
from pathlib import Path
from typing import Any


def now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def load_policy(claude_home: Path) -> dict[str, Any]:
    path = claude_home / "policy" / "codex-automations.json"
    if path.exists():
        return json.loads(path.read_text())
    return {
        "version": 1,
        "automations": [
            {
                "id": "compound-brain-runtime-heartbeat",
                "name": "Compound Runtime Heartbeat",
                "status": "ACTIVE",
                "rrule": "RRULE:FREQ=HOURLY;INTERVAL=6",
                "execution_environment": "local",
                "prompt": "Run the shared compound-brain runtime heartbeat. Execute `python3 ~/.claude/scripts/project_runtime_event.py --event cron --all-activated --json-output`, review blocked or failed repos, and summarize only actionable findings for the inbox.",
            },
            {
                "id": "compound-brain-skill-radar",
                "name": "Compound Skill Radar",
                "status": "ACTIVE",
                "rrule": "RRULE:FREQ=HOURLY;INTERVAL=12",
                "execution_environment": "local",
                "prompt": "Run the shared compound-brain skill radar refresh. Execute `python3 ~/.claude/scripts/skill_radar_refresh.py --json-output`, inspect new GitHub-derived candidates and project-tip signals, and summarize which skill proposals look worth reviewing next.",
            },
        ],
    }


def infer_repo_root(repo_root: Path | None) -> Path:
    if repo_root is None:
        return Path.cwd().resolve()
    return repo_root.resolve()


def automation_dir(codex_home: Path, automation_id: str) -> Path:
    return codex_home / "automations" / automation_id


def load_existing_automation(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return tomllib.loads(path.read_text())


def render_automation_toml(payload: dict[str, Any]) -> str:
    cwds = payload.get("cwds", [])
    lines = [
        f'version = {int(payload.get("version", 1))}',
        f'id = "{payload["id"]}"',
        f'name = "{payload["name"]}"',
        f'prompt = {json.dumps(payload["prompt"])}',
        f'status = "{payload["status"]}"',
        f'rrule = "{payload["rrule"]}"',
        f'execution_environment = "{payload["execution_environment"]}"',
        "cwds = [" + ", ".join(json.dumps(str(item)) for item in cwds) + "]",
        f'created_at = {int(payload["created_at"])}',
        f'updated_at = {int(payload["updated_at"])}',
        "",
    ]
    return "\n".join(lines)


def ensure_managed_automations(
    *,
    codex_home: Path,
    claude_home: Path,
    repo_root: Path | None = None,
) -> list[dict[str, Any]]:
    codex_home = codex_home.resolve()
    claude_home = claude_home.resolve()
    repo_root = infer_repo_root(repo_root)
    policy = load_policy(claude_home)
    created: list[dict[str, Any]] = []

    for spec in policy.get("automations", []):
        automation_id = str(spec["id"])
        directory = automation_dir(codex_home, automation_id)
        path = directory / "automation.toml"
        existing = load_existing_automation(path)
        created_at = int(existing.get("created_at", now_ms()))
        payload = {
            "version": 1,
            "id": automation_id,
            "name": str(spec["name"]),
            "prompt": str(spec["prompt"]),
            "status": str(spec.get("status", "ACTIVE")),
            "rrule": str(spec["rrule"]),
            "execution_environment": str(spec.get("execution_environment", "local")),
            "cwds": [str(repo_root)],
            "created_at": created_at,
            "updated_at": now_ms(),
        }
        directory.mkdir(parents=True, exist_ok=True)
        path.write_text(render_automation_toml(payload))
        created.append(payload)
    return created
