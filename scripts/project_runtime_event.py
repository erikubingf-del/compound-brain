#!/usr/bin/env python3
"""Shared repo event runtime for session hooks and cron-driven autoimprovement."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.lib.autonomy_depth import (
        apply_governor_to_depth_state,
        load_global_policy,
        load_repo_depth_state,
        required_context_files,
    )
    from scripts.lib.department_arbitration import arbitrate_departments
    from scripts.lib.runtime_heartbeat import RuntimeHeartbeatStore
    from scripts.lib.runtime_governor import (
        allowed_actions_for_event,
        build_context_snapshot,
        build_runtime_governor,
        build_runtime_packet,
        choose_lead_department,
        choose_supporting_departments,
    )
    from scripts.lib.skill_inventory import refresh_repo_skill_state
    from scripts.project_auditor import audit_project
    from scripts.project_intelligence import run_for_project
    from scripts.probability_engine import ProjectState, rank_actions
    from scripts.run_project_llm_cron import run_project_cron
    from scripts.update_architecture_scorecard import main as update_architecture_scorecard_main
except ModuleNotFoundError:
    from lib.autonomy_depth import (
        apply_governor_to_depth_state,
        load_global_policy,
        load_repo_depth_state,
        required_context_files,
    )
    from lib.department_arbitration import arbitrate_departments
    from lib.runtime_heartbeat import RuntimeHeartbeatStore
    from lib.runtime_governor import (
        allowed_actions_for_event,
        build_context_snapshot,
        build_runtime_governor,
        build_runtime_packet,
        choose_lead_department,
        choose_supporting_departments,
    )
    from lib.skill_inventory import refresh_repo_skill_state
    from project_auditor import audit_project
    from project_intelligence import run_for_project
    from probability_engine import ProjectState, rank_actions
    from run_project_llm_cron import run_project_cron
    from update_architecture_scorecard import main as update_architecture_scorecard_main


def claude_home_dir() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".claude"


def activation_registry_path() -> Path:
    return claude_home_dir() / "registry" / "activated-projects.json"


def heartbeat_store() -> RuntimeHeartbeatStore:
    root = claude_home_dir() / "registry"
    return RuntimeHeartbeatStore(
        heartbeat_root=root / "runtime-heartbeats",
        lock_root=root / "runtime-locks",
    )


def load_registry() -> list[dict[str, Any]]:
    path = activation_registry_path()
    if not path.exists():
        return []
    payload = json.loads(path.read_text())
    return list(payload.get("projects", []))


def is_activated_repo(project_dir: Path) -> bool:
    return (project_dir / ".brain").exists() and (project_dir / ".claude" / "settings.local.json").exists()


def audit_is_due(project_dir: Path, max_age_days: int = 7) -> bool:
    audit_path = project_dir / ".brain" / "knowledge" / "areas" / "project-audit.md"
    if not audit_path.exists():
        return True
    age_days = (datetime.now(timezone.utc).timestamp() - audit_path.stat().st_mtime) / 86400
    return age_days >= max_age_days


def refresh_ranked_actions(project_dir: Path) -> dict[str, Any]:
    state = ProjectState.from_brain(project_dir)
    result = rank_actions(state)
    return {
        "top_action": result.top_action.title,
        "top_action_category": result.top_action.category,
        "goal": result.goal,
    }


def maybe_update_scorecard(project_dir: Path) -> bool:
    if not (project_dir / ".brain" / "architecture" / "evaluator.md").exists():
        return False
    previous_argv = list(os.sys.argv)
    try:
        os.sys.argv = [
            "update_architecture_scorecard.py",
            "--repo-root",
            str(project_dir),
        ]
        update_architecture_scorecard_main()
        return True
    finally:
        os.sys.argv = previous_argv


def classify_exception(exc: Exception) -> str:
    return exc.__class__.__name__


def run_project_runtime_event(project_dir: Path, event: str) -> dict[str, Any]:
    project_dir = project_dir.resolve()
    if not is_activated_repo(project_dir):
        return {"status": "skipped", "reason": "repo-not-activated", "event": event}

    store = heartbeat_store()
    acquired, lock_info = store.acquire_lock(project_dir, event)
    if not acquired:
        return {
            "status": "locked",
            "reason": "runtime-lock-active",
            "event": event,
            "lock": lock_info,
        }

    start = time.monotonic()
    store.mark_start(project_dir, event)
    attempts = 2 if event == "cron" else 1
    attempt = 0
    try:
        while attempt < attempts:
            attempt += 1
            try:
                policy = load_global_policy(claude_home_dir())
                depth_state = load_repo_depth_state(project_dir, policy)
                approval_state_path = project_dir / ".brain" / "state" / "approval-state.json"
                approval_state = (
                    json.loads(approval_state_path.read_text())
                    if approval_state_path.exists()
                    else {"state": "inactive", "pending": []}
                )
                settings_path = project_dir / ".claude" / "settings.local.json"
                enabled_departments = []
                if settings_path.exists():
                    settings = json.loads(settings_path.read_text())
                    enabled_departments = list(settings.get("enabledDepartments", []))
                if not enabled_departments:
                    enabled_departments = [path.stem for path in (project_dir / ".claude" / "departments").glob("*.md")]

                audit_refreshed = False
                if event in {"session-start", "cron"} and audit_is_due(project_dir):
                    audit_refreshed = audit_project(project_dir, force=True)

                skills = refresh_repo_skill_state(project_dir, claude_home=claude_home_dir())
                ranking = refresh_ranked_actions(project_dir)
                project_state = ProjectState.from_brain(project_dir)
                lead_department = choose_lead_department(enabled_departments, ranking["top_action_category"], event)
                supporting_departments = choose_supporting_departments(enabled_departments, lead_department)
                agreement = arbitrate_departments(
                    repo=project_dir,
                    event=event,
                    current_depth=int(depth_state["current_depth"]),
                    lead_department=lead_department,
                    supporting_departments=supporting_departments,
                    top_action_category=ranking["top_action_category"],
                    approval_state=approval_state,
                )
                required_files = required_context_files(
                    project_dir,
                    event=event,
                    depth=int(depth_state["current_depth"]),
                    lead_department=lead_department,
                    claude_home=claude_home_dir(),
                )
                context_snapshot = build_context_snapshot(
                    project_dir,
                    event=event,
                    current_depth=int(depth_state["current_depth"]),
                    required_files=required_files,
                )
                governor = build_runtime_governor(
                    repo=project_dir,
                    event=event,
                    current_depth=int(depth_state["current_depth"]),
                    approval_state=approval_state,
                    context_snapshot=context_snapshot,
                    skill_state=skills,
                    heartbeat_record=store.load(project_dir),
                    policy=policy,
                    validation_success=project_state.test_pass_rate,
                    agreement=agreement,
                )
                depth_state = apply_governor_to_depth_state(
                    project_dir,
                    policy,
                    depth_state,
                    governor,
                    approval_state,
                )
                if int(depth_state["current_depth"]) != context_snapshot["current_depth"]:
                    required_files = required_context_files(
                        project_dir,
                        event=event,
                        depth=int(depth_state["current_depth"]),
                        lead_department=lead_department,
                        claude_home=claude_home_dir(),
                    )
                    context_snapshot = build_context_snapshot(
                        project_dir,
                        event=event,
                        current_depth=int(depth_state["current_depth"]),
                        required_files=required_files,
                    )
                    governor = build_runtime_governor(
                        repo=project_dir,
                        event=event,
                        current_depth=int(depth_state["current_depth"]),
                        approval_state=approval_state,
                        context_snapshot=context_snapshot,
                        skill_state=skills,
                        heartbeat_record=store.load(project_dir),
                        policy=policy,
                        validation_success=project_state.test_pass_rate,
                        agreement=agreement,
                    )

                allowed_actions, blocked_actions = allowed_actions_for_event(event, int(depth_state["current_depth"]))
                if agreement["result"] in {"object", "escalate"}:
                    allowed_actions = [item for item in allowed_actions if item != "bounded-edit"]
                    blocked_actions = list(dict.fromkeys([*blocked_actions, "bounded-edit"]))
                build_runtime_packet(
                    repo=project_dir,
                    event=event,
                    current_depth=int(depth_state["current_depth"]),
                    lead_department=lead_department,
                    supporting_departments=supporting_departments,
                    goal=ranking["goal"],
                    top_action=ranking["top_action"],
                    approval_state=approval_state,
                    skill_state=skills,
                    context_snapshot=context_snapshot,
                    allowed_actions=allowed_actions,
                    blocked_actions=blocked_actions,
                    do_not_repeat=[f"Do not repeat {item}" for item in approval_state.get("pending", [])][:2],
                    agreement=agreement,
                )

                if not context_snapshot["context_ok"]:
                    duration = time.monotonic() - start
                    summary = "blocked-context"
                    store.mark_success(project_dir, event, duration_seconds=duration, summary=summary)
                    return {
                        "status": "blocked",
                        "reason": "missing-context",
                        "event": event,
                        "current_depth": depth_state["current_depth"],
                        "missing_context_files": context_snapshot["missing_context_files"],
                    }

                brief = run_for_project(project_dir, dry_run=False)
                runtime: dict[str, Any] = {
                    "status": "ok",
                    "event": event,
                    "attempt": attempt,
                    "audit_refreshed": audit_refreshed,
                    "brief_written": bool(brief is not None),
                    "top_action": ranking["top_action"],
                    "goal": ranking["goal"],
                    "current_depth": depth_state["current_depth"],
                    "lead_department": lead_department,
                    "department_agreement": agreement["result"],
                    "skill_active_count": len(skills["active"]),
                    "skill_missing_count": len(skills["missing"]),
                    "skill_materialized_count": len(skills["materialized"]),
                    "trust_score": governor["trust_score"],
                }

                if event == "cron":
                    if agreement["result"] in {"object", "escalate"}:
                        summary = f"planning-only arbitration={agreement['result']}"
                        rc = 0
                    else:
                        summary, rc = run_project_cron(
                            project_dir,
                            dry_run=False,
                            refresh_skills=False,
                            current_depth=int(depth_state["current_depth"]),
                            lead_department=lead_department,
                            supporting_departments=supporting_departments,
                        )
                        summary = f"{summary}, arbitration={agreement['result']}"
                    runtime["cron_summary"] = summary
                    runtime["cron_rc"] = rc
                    if rc != 0:
                        raise RuntimeError(f"project-cron-rc-{rc}")

                if event == "stop":
                    runtime["scorecard_updated"] = maybe_update_scorecard(project_dir)

                duration = time.monotonic() - start
                summary = runtime.get("cron_summary") or runtime.get("top_action")
                store.mark_success(project_dir, event, duration_seconds=duration, summary=str(summary))
                return runtime
            except Exception as exc:
                if attempt < attempts:
                    continue
                duration = time.monotonic() - start
                store.mark_failure(
                    project_dir,
                    event,
                    error_class=classify_exception(exc),
                    error_message=str(exc),
                    duration_seconds=duration,
                )
                return {
                    "status": "failed",
                    "reason": classify_exception(exc),
                    "message": str(exc),
                    "event": event,
                    "attempt": attempt,
                }
    finally:
        store.release_lock(project_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run compound-brain repo runtime for a hook or cron event.")
    parser.add_argument("--project-dir", help="Single activated project")
    parser.add_argument("--event", choices=["session-start", "stop", "cron"], required=True)
    parser.add_argument("--all-activated", action="store_true", help="Run for all activated projects from the registry")
    args = parser.parse_args()

    if args.all_activated:
        projects = [Path(item["repo_path"]).resolve() for item in load_registry()]
    elif args.project_dir:
        projects = [Path(args.project_dir).resolve()]
    else:
        projects = [Path.cwd().resolve()]

    for project_dir in projects:
        result = run_project_runtime_event(project_dir, args.event)
        print(
            f"[project-runtime:{args.event}] {project_dir}: "
            f"{json.dumps(result, sort_keys=True)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
