from __future__ import annotations

from datetime import date, datetime, timezone
import json
from pathlib import Path
from typing import Any


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def relative_paths(repo: Path, paths: list[Path]) -> list[str]:
    repo = repo.resolve()
    result = []
    for path in paths:
        try:
            result.append(str(path.resolve().relative_to(repo)))
        except Exception:
            result.append(str(path))
    return result


def build_context_snapshot(
    repo: Path,
    event: str,
    current_depth: int,
    required_files: list[Path],
) -> dict[str, Any]:
    loaded: list[Path] = []
    missing: list[Path] = []
    for path in required_files:
        if path.exists():
            path.read_text(encoding="utf-8", errors="replace")
            loaded.append(path)
        else:
            missing.append(path)

    payload = {
        "version": 1,
        "generated_at": now_utc(),
        "event": event,
        "current_depth": current_depth,
        "required_context_files": relative_paths(repo, required_files),
        "loaded_context_files": relative_paths(repo, loaded),
        "missing_context_files": relative_paths(repo, missing),
        "context_ok": not missing,
    }
    state_path = repo / ".brain" / "state" / "context-snapshot.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2) + "\n")
    return payload


def heartbeat_score(record: dict[str, Any]) -> float:
    cron = dict(record.get("events", {}).get("cron", {}))
    status = cron.get("status")
    if status == "ok":
        return 1.0
    if status == "running":
        return 0.85
    if status == "failed":
        return 0.2
    if status == "never-run":
        return 0.7
    return 0.75


def department_health_score(repo: Path) -> tuple[float, dict[str, list[str]]]:
    state_dir = repo / ".brain" / "state" / "departments"
    if not state_dir.exists():
        summary = {
            "healthy_departments": [],
            "blocked_departments": [],
            "low_confidence_departments": [],
        }
        return 0.5, summary

    healthy: list[str] = []
    blocked: list[str] = []
    low_confidence: list[str] = []
    total = 0
    for path in sorted(state_dir.glob("*.json")):
        payload = json.loads(path.read_text())
        total += 1
        status = payload.get("status")
        confidence = float(payload.get("confidence_score", 0.0))
        if status in {"ready", "ok", "idle", "queued", "consulted"}:
            healthy.append(path.stem)
        if status in {"blocked", "failed"}:
            blocked.append(path.stem)
        if confidence < 0.35:
            low_confidence.append(path.stem)
    score = len(healthy) / max(total, 1)
    score -= min(len(blocked) / max(total, 1), 1.0) * 0.4
    score = max(0.0, min(score, 1.0))
    summary = {
        "healthy_departments": healthy,
        "blocked_departments": blocked,
        "low_confidence_departments": low_confidence,
    }
    return score, summary


def evaluator_score(repo: Path) -> float:
    results_path = repo / ".brain" / "autoresearch" / "results.jsonl"
    if not results_path.exists():
        return 0.5
    keeps = 0
    total = 0
    for line in results_path.read_text().splitlines()[-20:]:
        if not line.strip():
            continue
        payload = json.loads(line)
        total += 1
        if payload.get("status") in {"kept", "baseline-recorded"}:
            keeps += 1
    if total == 0:
        return 0.5
    return keeps / total


def load_previous_governor(repo: Path) -> dict[str, Any]:
    path = repo / ".brain" / "state" / "runtime-governor.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def compute_trend(scores: list[int]) -> str:
    if len(scores) < 2:
        return "stable"
    delta = scores[-1] - scores[-2]
    if delta >= 3:
        return "improving"
    if delta <= -3:
        return "falling"
    return "stable"


def compute_history(
    previous: dict[str, Any],
    *,
    trust_score: int,
    current_depth: int,
    healthy_cycle: bool,
) -> dict[str, Any]:
    history = dict(previous.get("history", {}))
    recent_scores = [int(item) for item in history.get("recent_trust_scores", [])][-5:]
    recent_scores.append(trust_score)
    streak = int(history.get("healthy_run_streak", 0))
    streak = streak + 1 if healthy_cycle else 0
    return {
        "recent_trust_scores": recent_scores,
        "healthy_run_streak": streak,
        "trend": compute_trend(recent_scores),
        "last_depth_observed": current_depth,
    }


def build_runtime_governor(
    repo: Path,
    event: str,
    current_depth: int,
    approval_state: dict[str, Any],
    context_snapshot: dict[str, Any],
    skill_state: dict[str, Any],
    heartbeat_record: dict[str, Any],
    policy: dict[str, Any],
    validation_success: float,
    agreement: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context_compliance = 1.0 if context_snapshot.get("context_ok") else 0.0
    pending = list(approval_state.get("pending", []))
    approval_health = 1.0 if not pending or current_depth <= 2 else 0.2
    heartbeat_reliability = heartbeat_score(heartbeat_record)
    evaluator_success = evaluator_score(repo)
    department_health, department_summary = department_health_score(repo)
    active = len(skill_state.get("active", []))
    missing = len(skill_state.get("missing", []))
    skill_coverage = active / max(active + missing, 1)
    user_alignment = 0.9 if not pending else 0.7

    repeated_failure_penalty = min(
        int(dict(heartbeat_record.get("events", {}).get("cron", {})).get("consecutive_failures", 0)) * 3,
        15,
    )
    drift_penalty = 5 if pending and current_depth > 2 else 0
    agreement_result = str((agreement or {}).get("result", "agree"))
    if agreement_result in {"object", "escalate"}:
        drift_penalty += 7
    protected_surface_penalty = 0
    context_skip_penalty = 25 if not context_snapshot.get("context_ok") else 0

    trust_score = int(
        round(
            20 * context_compliance
            + 15 * approval_health
            + 15 * heartbeat_reliability
            + 20 * validation_success
            + 10 * evaluator_success
            + 10 * department_health
            + 5 * skill_coverage
            + 5 * user_alignment
            - repeated_failure_penalty
            - drift_penalty
            - protected_surface_penalty
            - context_skip_penalty
        )
    )
    trust_score = max(0, min(trust_score, 100))
    stay_floor = int(policy.get("stay_floors", {}).get(str(current_depth), 0))
    healthy_cycle = (
        context_snapshot.get("context_ok")
        and trust_score >= stay_floor
        and not pending
        and agreement_result not in {"object", "escalate"}
        and repeated_failure_penalty == 0
        and context_skip_penalty == 0
    )
    previous = load_previous_governor(repo)
    history = compute_history(
        previous,
        trust_score=trust_score,
        current_depth=current_depth,
        healthy_cycle=healthy_cycle,
    )

    readiness = {
        "can_raise_to_3": trust_score >= int(policy.get("raise_thresholds", {}).get("3", 60)),
        "can_raise_to_4": trust_score >= int(policy.get("raise_thresholds", {}).get("4", 75)),
        "can_raise_to_5": trust_score >= int(policy.get("raise_thresholds", {}).get("5", 90)),
    }
    reasons = []
    if context_snapshot.get("context_ok"):
        reasons.append("context packet complete")
    else:
        reasons.append("required context missing")
    if pending:
        reasons.append("strategic approvals pending")
    if missing:
        reasons.append("skill coverage incomplete")
    if heartbeat_reliability >= 0.85:
        reasons.append("heartbeat healthy")
    if agreement_result in {"agree-with-constraints", "escalate"}:
        reasons.append(f"department agreement={agreement_result}")

    payload = {
        "version": 1,
        "generated_at": now_utc(),
        "event": event,
        "trust_score": trust_score,
        "components": {
            "context_compliance": round(context_compliance, 2),
            "approval_health": round(approval_health, 2),
            "heartbeat_reliability": round(heartbeat_reliability, 2),
            "validation_success": round(validation_success, 2),
            "evaluator_success": round(evaluator_success, 2),
            "department_health": round(department_health, 2),
            "skill_coverage": round(skill_coverage, 2),
            "user_alignment": round(user_alignment, 2),
        },
        "penalties": {
            "repeated_failure_penalty": repeated_failure_penalty,
            "drift_penalty": drift_penalty,
            "protected_surface_penalty": protected_surface_penalty,
            "context_skip_penalty": context_skip_penalty,
        },
        "readiness": readiness,
        "reasons": reasons,
        "department_health": department_summary,
        "history": history,
        "agreement": agreement or {"result": "agree", "positions": {}, "constraints": [], "objections": []},
    }
    state_path = repo / ".brain" / "state" / "runtime-governor.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2) + "\n")

    department_health_path = repo / ".brain" / "state" / "department-health.json"
    department_health_path.write_text(json.dumps({"version": 1, "generated_at": now_utc(), **department_summary}, indent=2) + "\n")
    return payload


def choose_lead_department(
    departments: list[str],
    top_action_category: str,
    event: str,
) -> str:
    if not departments:
        return "architecture"
    category_map = {
        "docs": "product",
        "infra": "operations",
        "security": "operations",
        "research": "research",
        "feature": "engineering",
        "fix": "engineering",
        "test": "engineering",
        "debt": "engineering",
    }
    preferred = category_map.get(top_action_category, departments[0])
    if event == "stop":
        return "architecture" if "architecture" in departments else departments[0]
    if preferred in departments:
        return preferred
    return departments[0]


def choose_supporting_departments(departments: list[str], lead_department: str) -> list[str]:
    supporting: list[str] = []
    for candidate in ["architecture", "product", "operations", "research", "engineering"]:
        if candidate == lead_department:
            continue
        if candidate in departments:
            supporting.append(candidate)
        if len(supporting) >= 2:
            break
    return supporting


def allowed_actions_for_event(event: str, current_depth: int) -> tuple[list[str], list[str]]:
    allowed: list[str] = []
    blocked: list[str] = []
    if event == "session-start":
        allowed = ["refresh-audit", "refresh-brief", "refresh-skills", "planning"]
        if current_depth >= 3:
            allowed.append("queue-bounded-execution")
        else:
            blocked.append("bounded-edit")
        if current_depth < 4:
            blocked.append("autoresearch")
    elif event == "cron":
        if current_depth <= 2:
            allowed = ["planning-only", "skill-refresh", "architecture-review"]
            blocked = ["bounded-edit", "autoresearch"]
        else:
            allowed = ["bounded-edit", "validation", "skill-refresh"]
            if current_depth >= 4:
                allowed.append("autoresearch")
            else:
                blocked.append("autoresearch")
    elif event == "stop":
        allowed = ["learning-compression", "decision-capture", "skill-review"]
        if current_depth >= 4:
            allowed.append("scorecard-review")
    return allowed, blocked


def build_runtime_packet(
    repo: Path,
    event: str,
    current_depth: int,
    lead_department: str,
    supporting_departments: list[str],
    goal: str,
    top_action: str,
    approval_state: dict[str, Any],
    skill_state: dict[str, Any],
    context_snapshot: dict[str, Any],
    allowed_actions: list[str],
    blocked_actions: list[str],
    do_not_repeat: list[str],
    agreement: dict[str, Any] | None = None,
    execution_mode: str = "one-shot",
    ralph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "version": 1,
        "generated_at": now_utc(),
        "event": event,
        "repo": repo.resolve().name,
        "current_depth": current_depth,
        "lead_department": lead_department,
        "supporting_departments": supporting_departments,
        "goal": goal,
        "top_action": top_action,
        "approvals": {
            "state": approval_state.get("state", "inactive"),
            "pending": list(approval_state.get("pending", [])),
        },
        "active_skills": [item["title"] for item in skill_state.get("active", [])],
        "missing_skills": [item["title"] for item in skill_state.get("missing", [])],
        "do_not_repeat": do_not_repeat,
        "allowed_actions": allowed_actions,
        "blocked_actions": blocked_actions,
        "execution_mode": execution_mode,
        "ralph": ralph or {"mode": execution_mode, "eligible": False, "reasons": []},
        "department_agreement": {
            "result": (agreement or {}).get("result", "agree"),
            "positions": (agreement or {}).get("positions", {}),
            "constraints": list((agreement or {}).get("constraints", [])),
            "objections": list((agreement or {}).get("objections", [])),
        },
        "required_context_files": list(context_snapshot.get("required_context_files", [])),
        "loaded_context_files": list(context_snapshot.get("loaded_context_files", [])),
        "context_ok": bool(context_snapshot.get("context_ok", False)),
    }
    state_path = repo / ".brain" / "state" / "runtime-packet.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2) + "\n")
    return payload


def operator_mode(
    approval_state: dict[str, Any],
    allowed_actions: list[str],
    blocked_actions: list[str],
    context_snapshot: dict[str, Any] | None,
    agreement: dict[str, Any] | None,
) -> tuple[str, list[str]]:
    blocked_by = list(approval_state.get("pending", []))
    if context_snapshot is not None and not context_snapshot.get("context_ok", True):
        blocked_by.append("missing_context")
    agreement_result = str((agreement or {}).get("result", "agree"))
    if agreement_result in {"object", "escalate"}:
        blocked_by.append(f"department_{agreement_result}")
    if "bounded-edit" in blocked_actions and "bounded-edit" not in allowed_actions and "planning_only" not in blocked_by:
        blocked_by.append("planning_only")

    if blocked_by:
        if any(item.startswith("department_") or item == "missing_context" for item in blocked_by):
            return "blocked", list(dict.fromkeys(blocked_by))
        return "awaiting-approval", list(dict.fromkeys(blocked_by))
    if "bounded-edit" in allowed_actions:
        return "ready-to-execute", []
    return "planning", []


def build_operator_recommendation(
    repo: Path,
    event: str,
    current_depth: int,
    goal: str,
    top_action: str,
    lead_department: str,
    supporting_departments: list[str],
    approval_state: dict[str, Any],
    governor: dict[str, Any],
    skill_state: dict[str, Any],
    allowed_actions: list[str],
    blocked_actions: list[str],
    agreement: dict[str, Any] | None = None,
    context_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    mode, blocked_by = operator_mode(
        approval_state=approval_state,
        allowed_actions=allowed_actions,
        blocked_actions=blocked_actions,
        context_snapshot=context_snapshot,
        agreement=agreement,
    )
    active_departments = [lead_department, *supporting_departments]
    active_departments = list(dict.fromkeys([item for item in active_departments if item]))
    missing_skills = [item["title"] for item in skill_state.get("missing", [])]
    active_skills = [item["title"] for item in skill_state.get("active", [])]
    new_opportunities = [
        {
            "title": str(item["title"]),
            "capability": str(item.get("capability", "")),
            "department": str(item.get("department", lead_department)),
            "source": str(item.get("source", "")),
            "score": item.get("score"),
        }
        for item in skill_state.get("recommended", [])[:3]
        if item.get("title")
    ]
    constraints = list((agreement or {}).get("constraints", []))[:3]
    objections = list((agreement or {}).get("objections", []))[:3]
    reasons = list(governor.get("reasons", []))[:4]
    trust_score = int(governor.get("trust_score", 0))

    rationale: list[str] = []
    rationale.extend(reasons[:2])
    if constraints:
        rationale.append(f"constraints: {'; '.join(constraints)}")
    if objections:
        rationale.append(f"objections: {'; '.join(objections)}")
    if missing_skills:
        rationale.append(f"missing skills: {', '.join(missing_skills[:3])}")
    if not rationale:
        rationale.append("bounded action available")

    payload = {
        "version": 1,
        "generated_at": now_utc(),
        "event": event,
        "repo": repo.resolve().name,
        "current_depth": current_depth,
        "mode": mode,
        "goal": goal,
        "recommended_next_action": top_action,
        "active_departments": active_departments,
        "lead_department": lead_department,
        "supporting_departments": supporting_departments,
        "blocked_by": blocked_by,
        "allowed_actions": allowed_actions,
        "blocked_actions": blocked_actions,
        "trust_score": trust_score,
        "active_skills": active_skills,
        "missing_skills": missing_skills,
        "new_opportunities": new_opportunities,
        "rationale": rationale,
    }

    state_path = repo / ".brain" / "state" / "operator-recommendation.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2) + "\n")

    latest_path = repo / ".brain" / "knowledge" / "daily" / "operator_brief_latest.md"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    bullet_lines = [
        f"- Mode: `{mode}`",
        f"- Goal: {goal}",
        f"- Recommended next action: {top_action}",
        f"- Lead department: `{lead_department}`",
        f"- Active departments: {', '.join(f'`{item}`' for item in active_departments)}",
        f"- Trust score: {trust_score}",
    ]
    if blocked_by:
        bullet_lines.append(f"- Blocked by: {', '.join(f'`{item}`' for item in blocked_by)}")
    if missing_skills:
        bullet_lines.append(f"- Missing skills: {', '.join(f'`{item}`' for item in missing_skills[:3])}")
    if new_opportunities:
        bullet_lines.append(
            "- New opportunities: "
            + ", ".join(
                f"`{item['title']}` ({item['department'] or lead_department})"
                for item in new_opportunities
            )
        )
    if rationale:
        bullet_lines.append(f"- Why now: {' | '.join(rationale)}")
    latest_path.write_text(
        f"# Operator Brief — {repo.name}\n\n"
        f"Generated: {now_utc()}\n\n"
        + "\n".join(bullet_lines)
        + "\n"
    )
    return payload
