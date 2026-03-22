from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


OPS_VETO_CATEGORIES = {"infra", "security", "runtime", "deploy", "ops"}
ARCH_VETO_CATEGORIES = {"infra", "security", "architecture", "control-plane", "migration"}


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_department_state(repo: Path, department: str) -> dict[str, Any]:
    path = repo / ".brain" / "state" / "departments" / f"{department}.json"
    if not path.exists():
        return {
            "department": department,
            "status": "unknown",
            "confidence_score": 0.5,
            "last_outcome": "not-run",
        }
    payload = json.loads(path.read_text())
    payload.setdefault("department", department)
    payload.setdefault("status", "unknown")
    payload.setdefault("confidence_score", 0.5)
    payload.setdefault("last_outcome", "not-run")
    return payload


def department_objects_on_category(department: str, category: str) -> bool:
    if department == "operations":
        return category in OPS_VETO_CATEGORIES
    if department == "architecture":
        return category in ARCH_VETO_CATEGORIES
    return False


def position_for_department(
    department: str,
    state: dict[str, Any],
    *,
    lead_department: str,
    top_action_category: str,
    approval_pending: bool,
) -> tuple[str, str]:
    status = str(state.get("status", "unknown"))
    confidence = float(state.get("confidence_score", 0.5))

    if department == lead_department:
        if status in {"blocked", "failed"} or confidence < 0.25:
            return "escalate", f"{department} cannot safely own the action"
        return "agree", f"{department} owns the current action"

    if approval_pending and department_objects_on_category(department, top_action_category):
        return "object", f"{department} requires strategic approval before {top_action_category} work"

    if status in {"blocked", "failed"}:
        if department_objects_on_category(department, top_action_category):
            return "object", f"{department} is blocked for {top_action_category} work"
        return "escalate", f"{department} is blocked"

    if confidence < 0.35:
        if department_objects_on_category(department, top_action_category):
            return "object", f"{department} confidence is too low for {top_action_category} work"
        return "escalate", f"{department} confidence is too low"

    if department in {"architecture", "operations", "product", "research"}:
        return "agree-with-constraints", f"{department} adds constraints"
    return "agree", f"{department} agrees"


def arbitrate_departments(
    repo: Path,
    event: str,
    current_depth: int,
    lead_department: str,
    supporting_departments: list[str],
    top_action_category: str,
    approval_state: dict[str, Any],
) -> dict[str, Any]:
    repo = repo.resolve()
    pending = list(approval_state.get("pending", []))
    all_departments = [lead_department, *supporting_departments]
    positions: dict[str, str] = {}
    reasons: dict[str, str] = {}
    constraints: list[str] = []
    objections: list[str] = []

    for department in all_departments:
        state = load_department_state(repo, department)
        position, reason = position_for_department(
            department,
            state,
            lead_department=lead_department,
            top_action_category=top_action_category,
            approval_pending=bool(pending),
        )
        positions[department] = position
        reasons[department] = reason
        if position == "object":
            objections.append(f"{department}: {reason}")
        elif position in {"agree-with-constraints", "escalate"}:
            constraints.append(f"{department}: {reason}")

    result = "agree"
    if any(position == "object" for position in positions.values()) or any(
        position == "escalate" for position in positions.values()
    ):
        result = "escalate"
    elif any(position == "agree-with-constraints" for position in positions.values()):
        result = "agree-with-constraints"

    payload = {
        "version": 1,
        "generated_at": now_utc(),
        "event": event,
        "current_depth": current_depth,
        "lead_department": lead_department,
        "supporting_departments": supporting_departments,
        "top_action_category": top_action_category,
        "approval_pending": pending,
        "result": result,
        "positions": positions,
        "reasons": reasons,
        "constraints": constraints,
        "objections": objections,
    }
    path = repo / ".brain" / "state" / "department-agreement.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return payload
