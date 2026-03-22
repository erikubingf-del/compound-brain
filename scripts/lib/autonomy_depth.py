from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_policy() -> dict[str, Any]:
    return {
        "version": 1,
        "user_max_depth": 5,
        "default_repo_start_depth": 2,
        "auto_raise_enabled": True,
        "auto_lower_enabled": True,
        "require_confirmation_for_first_depth_5": True,
        "raise_thresholds": {"3": 60, "4": 75, "5": 90},
        "stay_floors": {"2": 25, "3": 50, "4": 68, "5": 85},
    }


def default_required_context() -> dict[str, Any]:
    return {
        "version": 1,
        "events": {
            "session-start": {
                "1": [
                    "CLAUDE.md",
                    ".brain/MEMORY.md",
                    ".brain/memory/project_context.md",
                    ".brain/memory/feedback_rules.md",
                ],
                "2": [
                    "CLAUDE.md",
                    ".brain/MEMORY.md",
                    ".brain/memory/project_context.md",
                    ".brain/memory/feedback_rules.md",
                    ".brain/state/action-queue.md",
                    ".brain/state/skills.json",
                    ".brain/knowledge/projects/{repo_name}.md",
                ],
                "3": [
                    "CLAUDE.md",
                    ".brain/MEMORY.md",
                    ".brain/memory/project_context.md",
                    ".brain/memory/feedback_rules.md",
                    ".brain/state/action-queue.md",
                    ".brain/state/skills.json",
                    ".brain/state/approval-state.json",
                    ".claude/settings.local.json",
                    ".claude/departments/{lead_department}.md",
                ],
                "4": [
                    "CLAUDE.md",
                    ".brain/MEMORY.md",
                    ".brain/memory/project_context.md",
                    ".brain/memory/feedback_rules.md",
                    ".brain/state/action-queue.md",
                    ".brain/state/skills.json",
                    ".brain/state/approval-state.json",
                    ".brain/state/runtime-governor.json",
                    ".claude/settings.local.json",
                    ".claude/departments/{lead_department}.md",
                    ".brain/autoresearch/program.md",
                ],
                "5": [
                    "CLAUDE.md",
                    ".brain/MEMORY.md",
                    ".brain/memory/project_context.md",
                    ".brain/memory/feedback_rules.md",
                    ".brain/state/action-queue.md",
                    ".brain/state/skills.json",
                    ".brain/state/approval-state.json",
                    ".brain/state/runtime-governor.json",
                    ".brain/state/department-health.json",
                    ".claude/settings.local.json",
                    ".claude/departments/{lead_department}.md",
                    ".brain/knowledge/departments/{lead_department}-sources.md",
                    ".brain/autoresearch/program.md",
                ],
            },
            "cron": {
                "2": [
                    ".brain/state/action-queue.md",
                    ".brain/state/skills.json",
                    ".brain/state/autonomy-depth.json",
                ],
                "3": [
                    ".brain/state/action-queue.md",
                    ".brain/state/skills.json",
                    ".brain/state/approval-state.json",
                    ".brain/state/autonomy-depth.json",
                    ".claude/settings.local.json",
                    ".claude/departments/{lead_department}.md",
                ],
                "4": [
                    ".brain/state/action-queue.md",
                    ".brain/state/skills.json",
                    ".brain/state/approval-state.json",
                    ".brain/state/autonomy-depth.json",
                    ".brain/state/runtime-governor.json",
                    ".claude/settings.local.json",
                    ".claude/departments/{lead_department}.md",
                    ".brain/autoresearch/program.md",
                ],
                "5": [
                    ".brain/state/action-queue.md",
                    ".brain/state/skills.json",
                    ".brain/state/approval-state.json",
                    ".brain/state/autonomy-depth.json",
                    ".brain/state/runtime-governor.json",
                    ".brain/state/department-health.json",
                    ".claude/settings.local.json",
                    ".claude/departments/{lead_department}.md",
                    ".brain/knowledge/departments/{lead_department}-sources.md",
                    ".brain/autoresearch/program.md",
                ],
            },
            "stop": {
                "2": [
                    ".brain/state/action-queue.md",
                    ".brain/state/skills.json",
                ],
                "3": [
                    ".brain/state/action-queue.md",
                    ".brain/state/skills.json",
                    ".brain/state/approval-state.json",
                    ".brain/state/runtime-governor.json",
                ],
                "4": [
                    ".brain/state/action-queue.md",
                    ".brain/state/skills.json",
                    ".brain/state/approval-state.json",
                    ".brain/state/runtime-governor.json",
                    ".brain/autoresearch/program.md",
                ],
                "5": [
                    ".brain/state/action-queue.md",
                    ".brain/state/skills.json",
                    ".brain/state/approval-state.json",
                    ".brain/state/runtime-governor.json",
                    ".brain/state/department-health.json",
                    ".brain/autoresearch/program.md",
                ],
            },
        },
    }


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def save_json(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return payload


def policy_dir(claude_home: Path) -> Path:
    return claude_home / "policy"


def ensure_global_policy(claude_home: Path) -> dict[str, Any]:
    policy_root = policy_dir(claude_home)
    policy_root.mkdir(parents=True, exist_ok=True)

    depth_path = policy_root / "autonomy-depth.json"
    if not depth_path.exists():
        save_json(depth_path, default_policy())

    context_path = policy_root / "required-context.json"
    if not context_path.exists():
        save_json(context_path, default_required_context())

    return load_json(depth_path, default_policy())


def load_global_policy(claude_home: Path) -> dict[str, Any]:
    return ensure_global_policy(claude_home)


def load_required_context(claude_home: Path) -> dict[str, Any]:
    ensure_global_policy(claude_home)
    return load_json(policy_dir(claude_home) / "required-context.json", default_required_context())


def initial_depth_for_repo(repo: Path, policy: dict[str, Any]) -> int:
    default_depth = int(policy.get("default_repo_start_depth", 2))
    if repo.resolve().name == "compound-brain":
        default_depth = max(default_depth, 4)
    return min(default_depth, int(policy.get("user_max_depth", 5)))


def initialize_repo_depth_state(repo: Path, policy: dict[str, Any]) -> dict[str, Any]:
    state_path = repo / ".brain" / "state" / "autonomy-depth.json"
    current = load_json(state_path, {})
    if current:
        return current

    current_depth = initial_depth_for_repo(repo, policy)
    payload = {
        "version": 1,
        "repo": repo.resolve().name,
        "current_depth": current_depth,
        "allowed_max_depth": int(policy.get("user_max_depth", 5)),
        "user_max_depth": int(policy.get("user_max_depth", 5)),
        "recommended_next_depth": min(current_depth + 1, int(policy.get("user_max_depth", 5))),
        "recommended_direction": "raise" if current_depth < int(policy.get("user_max_depth", 5)) else "stay",
        "recommendation_confidence": 0.6,
        "last_depth_change_at": now_utc(),
        "last_depth_change_reason": "activation-default",
        "consecutive_healthy_cycles": 0,
        "blocked_by": [],
        "raise_frozen_until": None,
    }
    return save_json(state_path, payload)


def load_repo_depth_state(repo: Path, policy: dict[str, Any]) -> dict[str, Any]:
    return initialize_repo_depth_state(repo, policy)


def save_repo_depth_state(repo: Path, payload: dict[str, Any]) -> dict[str, Any]:
    return save_json(repo / ".brain" / "state" / "autonomy-depth.json", payload)


def initialize_runtime_state(repo: Path, depth_state: dict[str, Any]) -> None:
    state_dir = repo / ".brain" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    save_json(
        state_dir / "runtime-governor.json",
        load_json(
            state_dir / "runtime-governor.json",
            {
                "version": 1,
                "generated_at": now_utc(),
                "trust_score": 50,
                "components": {},
                "penalties": {},
                "readiness": {},
                "reasons": ["Awaiting first runtime cycle."],
            },
        ),
    )
    save_json(
        state_dir / "runtime-packet.json",
        load_json(
            state_dir / "runtime-packet.json",
            {
                "version": 1,
                "generated_at": now_utc(),
                "event": "activation",
                "repo": repo.resolve().name,
                "current_depth": depth_state["current_depth"],
                "lead_department": None,
                "supporting_departments": [],
                "goal": "Pending strategic confirmation",
                "top_action": "Confirm project and department goals",
                "approvals": {"state": "awaiting-project-goal", "pending": ["project_goal", "department_goals"]},
                "active_skills": [],
                "missing_skills": [],
                "do_not_repeat": [],
                "allowed_actions": ["planning"],
                "blocked_actions": ["bounded-edit", "autoresearch"],
                "required_context_files": [],
                "loaded_context_files": [],
                "context_ok": False,
            },
        ),
    )
    save_json(
        state_dir / "context-snapshot.json",
        load_json(
            state_dir / "context-snapshot.json",
            {
                "version": 1,
                "generated_at": now_utc(),
                "event": "activation",
                "current_depth": depth_state["current_depth"],
                "required_context_files": [],
                "loaded_context_files": [],
                "missing_context_files": [],
                "context_ok": False,
            },
        ),
    )
    save_json(
        state_dir / "department-health.json",
        load_json(
            state_dir / "department-health.json",
            {
                "version": 1,
                "generated_at": now_utc(),
                "healthy_departments": [],
                "blocked_departments": [],
                "low_confidence_departments": [],
            },
        ),
    )
    save_json(
        state_dir / "department-agreement.json",
        load_json(
            state_dir / "department-agreement.json",
            {
                "version": 1,
                "generated_at": now_utc(),
                "result": "agree",
                "positions": {},
                "constraints": [],
                "objections": [],
            },
        ),
    )


def required_context_files(
    repo: Path,
    event: str,
    depth: int,
    lead_department: str,
    claude_home: Path,
) -> list[Path]:
    config = load_required_context(claude_home)
    event_rules = dict(config.get("events", {}).get(event, {}))
    if not event_rules:
        return []

    applicable_depth = max(
        (int(key) for key in event_rules.keys() if int(key) <= depth),
        default=min(int(key) for key in event_rules.keys()),
    )
    raw_files = event_rules[str(applicable_depth)]
    resolved = []
    for item in raw_files:
        rendered = item.format(repo_name=repo.resolve().name, lead_department=lead_department)
        resolved.append(repo / rendered)
    return resolved


def raise_cycle_requirement(next_depth: int) -> int:
    thresholds = {3: 3, 4: 5, 5: 10}
    return thresholds.get(next_depth, 999)


def apply_governor_to_depth_state(
    repo: Path,
    policy: dict[str, Any],
    depth_state: dict[str, Any],
    governor: dict[str, Any],
    approval_state: dict[str, Any],
) -> dict[str, Any]:
    current_depth = int(depth_state.get("current_depth", 2))
    trust_score = int(governor.get("trust_score", 0))
    pending = list(approval_state.get("pending", []))
    agreement_result = str(governor.get("agreement", {}).get("result", "agree"))
    history = dict(governor.get("history", {}))
    healthy_streak = int(history.get("healthy_run_streak", depth_state.get("consecutive_healthy_cycles", 0)))
    trend = str(history.get("trend", "stable"))
    blocked_by: list[str] = []
    reason = "steady"

    if governor.get("penalties", {}).get("context_skip_penalty", 0) > 0 and current_depth > 2:
        current_depth = 2
        blocked_by.append("context-snapshot")
        reason = "context-blocked"
        healthy_streak = 0
    elif pending and current_depth > 2:
        current_depth = 2
        blocked_by.extend(str(item) for item in pending)
        reason = "strategic-approval-pending"
        healthy_streak = 0
    else:
        stay_floor = int(policy.get("stay_floors", {}).get(str(current_depth), 0))
        severe_disagreement = agreement_result in {"object", "escalate"}
        if severe_disagreement:
            blocked_by.append(f"department-agreement:{agreement_result}")
        if current_depth > 2 and policy.get("auto_lower_enabled", True) and (
            trust_score < stay_floor or (severe_disagreement and trend == "falling")
        ):
            current_depth = max(2, current_depth - 1)
            reason = "trust-below-floor" if trust_score < stay_floor else "department-disagreement"
            healthy_streak = 0

    allowed_max = min(
        int(depth_state.get("allowed_max_depth", policy.get("user_max_depth", 5))),
        int(policy.get("user_max_depth", 5)),
    )
    current_depth = min(current_depth, allowed_max)

    recommended_direction = "stay"
    recommended_next_depth = current_depth
    confidence = 0.6
    next_depth = min(current_depth + 1, allowed_max)
    raise_threshold = int(policy.get("raise_thresholds", {}).get(str(next_depth), 999))
    enough_cycles = healthy_streak >= raise_cycle_requirement(next_depth)
    if (
        next_depth > current_depth
        and trust_score >= raise_threshold
        and not pending
        and agreement_result not in {"object", "escalate"}
        and trend != "falling"
    ):
        recommended_direction = "raise"
        recommended_next_depth = next_depth
        confidence = min(0.95, 0.5 + (trust_score / 200))
        if policy.get("auto_raise_enabled", True) and enough_cycles:
            current_depth = next_depth
            reason = "auto-raise"
    elif blocked_by or (
        current_depth > 2
        and (
            trust_score < int(policy.get("stay_floors", {}).get(str(current_depth), 0))
            or agreement_result in {"object", "escalate"}
            or trend == "falling"
        )
    ):
        recommended_direction = "lower"
        recommended_next_depth = max(2, current_depth - 1)
        confidence = 0.8

    depth_state["current_depth"] = current_depth
    depth_state["recommended_next_depth"] = recommended_next_depth
    depth_state["recommended_direction"] = recommended_direction
    depth_state["recommendation_confidence"] = round(confidence, 2)
    depth_state["allowed_max_depth"] = allowed_max
    depth_state["user_max_depth"] = int(policy.get("user_max_depth", 5))
    depth_state["blocked_by"] = blocked_by
    depth_state["consecutive_healthy_cycles"] = healthy_streak
    depth_state["last_depth_change_at"] = now_utc()
    depth_state["last_depth_change_reason"] = reason
    return save_repo_depth_state(repo, depth_state)
