from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_ralph_policy() -> dict[str, Any]:
    return {
        "version": 1,
        "enabled_for_compound_brain": True,
        "eligible_events": ["cron"],
        "min_depth": 4,
        "min_trust_score": 75,
        "required_healthy_streak": 3,
        "eligible_categories": ["feature", "debt", "research"],
        "preferred_agent": "codex",
        "default_prd_path": ".agents/tasks/prd-compound-brain-auto.json",
        "auto_create_prd": True,
    }


def load_ralph_policy(claude_home: Path) -> dict[str, Any]:
    policy_path = claude_home / "policy" / "ralph-policy.json"
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    if not policy_path.exists():
        policy_path.write_text(json.dumps(default_ralph_policy(), indent=2) + "\n")
        return default_ralph_policy()
    return json.loads(policy_path.read_text())


def build_ralph_decision(
    repo: Path,
    event: str,
    current_depth: int,
    top_action: str,
    top_action_category: str,
    approval_state: dict[str, Any],
    governor: dict[str, Any],
    agreement: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    repo = repo.resolve()
    reasons: list[str] = []
    if not policy.get("enabled_for_compound_brain", True):
        reasons.append("policy-disabled")
    if repo.name != "compound-brain":
        reasons.append("repo-not-self-hosting")
    if event not in list(policy.get("eligible_events", ["cron"])):
        reasons.append("event-not-eligible")
    if current_depth < int(policy.get("min_depth", 4)):
        reasons.append("depth-below-minimum")
    if approval_state.get("pending"):
        reasons.append("strategic-approval-pending")
    if str(agreement.get("result", "agree")) in {"object", "escalate"}:
        reasons.append("department-disagreement")
    trust_score = int(governor.get("trust_score", 0))
    if trust_score < int(policy.get("min_trust_score", 75)):
        reasons.append("trust-below-threshold")
    healthy_streak = int(dict(governor.get("history", {})).get("healthy_run_streak", 0))
    if healthy_streak < int(policy.get("required_healthy_streak", 3)):
        reasons.append("healthy-streak-too-short")
    if top_action_category not in list(policy.get("eligible_categories", [])):
        reasons.append("category-not-eligible")
    if not top_action.strip():
        reasons.append("missing-top-action")

    eligible = not reasons
    preferred_agent = os.environ.get(
        "COMPOUND_BRAIN_RALPH_AGENT",
        str(policy.get("preferred_agent", "codex")),
    )
    prd_path = repo / str(policy.get("default_prd_path", ".agents/tasks/prd-compound-brain-auto.json"))
    return {
        "mode": "ralph" if eligible else "one-shot",
        "eligible": eligible,
        "agent": preferred_agent,
        "prd_path": str(prd_path),
        "reasons": reasons or ["ralph-eligible"],
    }


def build_ralph_prd_payload(
    repo: Path,
    top_action: str,
    goal: str,
    quality_gates: list[str],
) -> dict[str, Any]:
    title = top_action.strip() or "Advance the orchestrator safely"
    return {
        "version": 1,
        "project": repo.resolve().name,
        "overview": goal,
        "goals": [
            goal,
            "Keep compound-brain self-hosting, evaluator-gated, and compatible across Claude and Codex.",
        ],
        "nonGoals": [
            "Do not bypass strategic approvals.",
            "Do not widen autonomy without trust and verification evidence.",
        ],
        "successMetrics": [
            "The selected story lands with deterministic verification evidence.",
            "The orchestrator remains aligned with the current project goal and evaluator.",
        ],
        "openQuestions": [],
        "stack": {
            "framework": "Python scripts plus markdown control planes",
            "hosting": "local runtime",
            "database": "file-based state",
            "auth": "not applicable",
        },
        "routes": [],
        "uiNotes": [],
        "dataModel": [
            {"entity": "RuntimeState", "fields": ["depth", "trust_score", "department_agreement"]},
        ],
        "importFormat": {
            "description": "Not applicable",
            "example": {},
        },
        "rules": [
            "Respect approval-state.json before changing strategy or evaluator surfaces.",
            "Prefer bounded, testable changes that keep Claude and Codex on one control plane.",
        ],
        "qualityGates": quality_gates,
        "stories": [
            {
                "id": "US-001",
                "title": title,
                "status": "open",
                "dependsOn": [],
                "description": (
                    "As the compound-brain maintainer, I want the orchestrator to improve one "
                    "bounded self-hosting lane so future sessions become more reliable."
                ),
                "acceptanceCriteria": [
                    f"Example: {title} is completed with the relevant files updated.",
                    "Negative case: if strategic approval becomes pending, stop and log the blocker instead of changing the runtime.",
                    "Relevant deterministic quality gates pass for the completed story.",
                ],
            }
        ],
    }


def ensure_ralph_prd(
    repo: Path,
    prd_path: Path,
    top_action: str,
    goal: str,
    quality_gates: list[str],
) -> Path:
    prd_path.parent.mkdir(parents=True, exist_ok=True)
    if prd_path.exists():
        existing = json.loads(prd_path.read_text())
        stories = list(existing.get("stories", []))
        if stories:
            first_story = dict(stories[0])
            if first_story.get("title") == top_action and first_story.get("status") in {"open", "in_progress"}:
                return prd_path

    payload = build_ralph_prd_payload(repo, top_action=top_action, goal=goal, quality_gates=quality_gates)
    prd_path.write_text(json.dumps(payload, indent=2) + "\n")
    return prd_path


def write_ralph_state(repo: Path, payload: dict[str, Any]) -> None:
    state_path = repo / ".brain" / "state" / "ralph-state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2) + "\n")


def run_ralph_loop(
    repo: Path,
    prd_path: Path,
    agent: str,
) -> dict[str, Any]:
    binary = shutil.which("ralph")
    if not binary:
        payload = {
            "version": 1,
            "generated_at": now_utc(),
            "mode": "ralph",
            "status": "unavailable",
            "agent": agent,
            "prd_path": str(prd_path),
            "reason": "ralph-not-installed",
        }
        write_ralph_state(repo, payload)
        return payload

    completed = subprocess.run(
        ["ralph", "build", "1", "--agent", agent, "--prd", str(prd_path)],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=False,
    )
    stdout = str(getattr(completed, "stdout", "") or "")
    stderr = str(getattr(completed, "stderr", "") or "")
    raw_returncode = getattr(completed, "returncode", 0)
    returncode = raw_returncode if isinstance(raw_returncode, int) else 0
    payload = {
        "version": 1,
        "generated_at": now_utc(),
        "mode": "ralph",
        "status": "executed" if returncode == 0 else "failed",
        "agent": agent,
        "prd_path": str(prd_path),
        "returncode": returncode,
        "stdout_tail": stdout.strip().splitlines()[-5:],
        "stderr_tail": stderr.strip().splitlines()[-5:],
    }
    write_ralph_state(repo, payload)
    return payload
