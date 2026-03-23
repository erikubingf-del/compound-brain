from __future__ import annotations

from datetime import date, datetime, timezone
import json
from pathlib import Path
from typing import Any


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    return json.loads(path.read_text())


def choose_bounded_action(repo: Path, department: str, top_action: str | None = None) -> str:
    if top_action:
        return top_action
    queue_path = repo / ".brain" / "state" / "action-queue.md"
    if queue_path.exists():
        for line in queue_path.read_text().splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                return stripped[2:]
    return f"Review {department} backlog"


def infer_execution_class(action: str, department: str) -> str:
    lowered = f"{department} {action}".lower()
    if department == "research" or any(token in lowered for token in {"research", "experiment", "hypothesis"}):
        return "research"
    if department == "product" or any(token in lowered for token in {"document", "docs", "brief", "copy"}):
        return "document"
    if department == "operations" or any(
        token in lowered for token in {"verify", "deploy", "release", "runtime", "ops", "infrastructure"}
    ):
        return "verify"
    return "implement"


def choose_verifier(lead_department: str, supporting_departments: list[str]) -> str:
    for candidate in ["operations", "architecture", "research", "product"]:
        if candidate in supporting_departments:
            return candidate
    return lead_department


def stage_summary(execution_class: str, action: str, goal: str) -> list[dict[str, str]]:
    return [
        {
            "class": "analyze",
            "instruction": f"Review prior failures, skills, and constraints before `{action}`.",
        },
        {
            "class": execution_class,
            "instruction": f"Advance the goal `{goal}` through `{action}`.",
        },
        {
            "class": "verify",
            "instruction": f"Verify `{action}` against the repo gates and expected outcome.",
        },
    ]


def missing_skills_for_department(skill_state: dict[str, Any], department: str) -> list[str]:
    missing = []
    for item in skill_state.get("missing", []):
        if str(item.get("department", "")) == department:
            missing.append(str(item.get("title", "")))
    return [item for item in missing if item]


def follow_up_actions_for_cycle(
    execution_class: str,
    supporting_departments: list[str],
    skill_state: dict[str, Any],
) -> list[str]:
    actions: list[str] = []
    if execution_class == "implement" and "product" in supporting_departments:
        actions.append("write-product-brief")
    if execution_class in {"implement", "research"} and "operations" in supporting_departments:
        actions.append("run-release-safety-review")
    for department in supporting_departments:
        for skill in missing_skills_for_department(skill_state, department):
            actions.append(f"skill-shopping:{department}:{skill}")
    return actions


def write_department_state(
    repo: Path,
    department: str,
    *,
    status: str,
    action: str,
    reason: str,
    confidence_score: float | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    state_path = repo / ".brain" / "state" / "departments" / f"{department}.json"
    payload = load_json(
        state_path,
        {
            "department": department,
            "status": "idle",
            "approval_state": "pending",
            "current_action": "",
            "active_hypothesis": "",
            "confidence_score": 0.0,
            "last_outcome": "not-run",
        },
    )
    payload["status"] = status
    payload["current_action"] = action
    payload["last_outcome"] = reason
    payload["last_run"] = now_utc()
    if confidence_score is not None:
        payload["confidence_score"] = round(confidence_score, 2)
    if extra:
        payload.update(extra)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2) + "\n")


def persist_mission_packet(
    repo: Path,
    department: str,
    *,
    current_depth: int,
    goal: str,
    action: str,
    execution_class: str,
    lead_department: str,
    supporting_departments: list[str],
    skill_state: dict[str, Any],
) -> Path:
    verifier = choose_verifier(lead_department, supporting_departments)
    stages = stage_summary(execution_class, action, goal or "advance the project goal")
    mission = {
        "version": 1,
        "generated_at": now_utc(),
        "department": department,
        "lead_department": lead_department,
        "supporting_departments": supporting_departments,
        "current_depth": current_depth,
        "goal": goal,
        "action": action,
        "execution_class": execution_class,
        "stages": [
            {
                "class": stages[0]["class"],
                "department": lead_department,
                "instruction": stages[0]["instruction"],
                "status": "queued",
            },
            {
                "class": stages[1]["class"],
                "department": lead_department,
                "instruction": stages[1]["instruction"],
                "status": "queued",
            },
            {
                "class": stages[2]["class"],
                "department": verifier,
                "instruction": stages[2]["instruction"],
                "status": "queued",
            },
        ],
        "handoff_departments": [verifier] if verifier != lead_department else [],
        "missing_support_skills": {
            item: missing_skills_for_department(skill_state, item) for item in supporting_departments
        },
    }
    mission_path = repo / ".brain" / "state" / "departments" / f"{department}-mission.json"
    mission_path.parent.mkdir(parents=True, exist_ok=True)
    mission_path.write_text(json.dumps(mission, indent=2) + "\n")
    return mission_path


def update_supporting_departments(
    repo: Path,
    *,
    lead_department: str,
    action: str,
    supporting_departments: list[str],
    handoff_departments: list[str],
) -> None:
    for department in supporting_departments:
        status = "queued" if department in handoff_departments else "consulted"
        reason = "mission-handoff" if department in handoff_departments else "mission-constraint"
        write_department_state(
            repo,
            department,
            status=status,
            action=f"Support {lead_department}: {action}",
            reason=reason,
            confidence_score=0.55 if status == "queued" else 0.6,
            extra={"linked_department": lead_department},
        )


def append_daily_summary(repo: Path, department: str, result: dict[str, Any]) -> None:
    daily_dir = repo / ".brain" / "knowledge" / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    daily_path = daily_dir / f"{date.today().isoformat()}.md"
    if not daily_path.exists():
        daily_path.write_text(f"# {date.today().isoformat()} — {repo.name}\n\n## Session Notes\n")
    detail = f"{result['action']}"
    if result.get("execution_class"):
        detail += f" [{result['execution_class']}]"
    if result.get("handoff_departments"):
        detail += f" -> handoff {', '.join(result['handoff_departments'])}"
    with daily_path.open("a") as handle:
        handle.write(
            f"- Department `{department}` -> {result['status']} ({result['reason']}): {detail}\n"
        )


def run_department_cycle(
    repo: Path,
    department: str,
    *,
    current_depth: int = 3,
    goal: str = "",
    top_action: str | None = None,
    supporting_departments: list[str] | None = None,
    skill_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    supporting_departments = list(supporting_departments or [])
    skill_state = skill_state or {"active": [], "missing": []}
    approval = load_json(
        repo / ".brain" / "state" / "approval-state.json",
        {"state": "inactive", "pending": []},
    )
    action = choose_bounded_action(repo, department, top_action=top_action)
    if approval.get("pending"):
        result = {
            "department": department,
            "status": "blocked",
            "reason": "approval-pending",
            "action": action,
            "execution_class": "analyze",
            "handoff_departments": [],
            "follow_up_actions": [],
        }
        write_department_state(
            repo,
            department,
            status="blocked",
            action=action,
            reason="approval-pending",
            confidence_score=0.15,
        )
        append_daily_summary(repo, department, result)
        return result

    execution_class = infer_execution_class(action, department)
    mission_path = persist_mission_packet(
        repo,
        department,
        current_depth=current_depth,
        goal=goal or "Advance the project goal",
        action=action,
        execution_class=execution_class,
        lead_department=department,
        supporting_departments=supporting_departments,
        skill_state=skill_state,
    )
    mission = json.loads(mission_path.read_text())
    handoff_departments = list(mission.get("handoff_departments", []))
    follow_up_actions = follow_up_actions_for_cycle(execution_class, supporting_departments, skill_state)
    write_department_state(
        repo,
        department,
        status="ready",
        action=action,
        reason="mission-queued",
        confidence_score=0.74 if execution_class == "implement" else 0.68,
        extra={
            "execution_class": execution_class,
            "mission_path": str(mission_path.relative_to(repo)),
            "handoff_departments": handoff_departments,
        },
    )
    update_supporting_departments(
        repo,
        lead_department=department,
        action=action,
        supporting_departments=supporting_departments,
        handoff_departments=handoff_departments,
    )

    result = {
        "department": department,
        "status": "ready",
        "reason": "mission-queued",
        "action": action,
        "execution_class": execution_class,
        "handoff_departments": handoff_departments,
        "follow_up_actions": follow_up_actions,
        "mission_path": str(mission_path.relative_to(repo)),
    }
    append_daily_summary(repo, department, result)
    return result
