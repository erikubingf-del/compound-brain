#!/usr/bin/env python3
"""activate_repo.py — preflight and registration entry point for alive repos."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from scripts.lib.autonomy_depth import (
        ensure_global_policy,
        initialize_repo_depth_state,
        initialize_runtime_state,
    )
    from scripts.lib.approval_state import ApprovalStateStore
    from scripts.lib.activation_registry import ActivationRegistry
    from scripts.lib.audit_packet import build_audit_packet
    from scripts.lib.repo_preview_cache import RepoPreviewCache
    from scripts.lib.repo_profile import build_department_surfaces, build_repo_profile, write_repo_profile
    from scripts.lib.skill_inventory import refresh_repo_skill_state
    from scripts.materialize_project_claude import materialize_project_claude
    from scripts.prepare_brain import prepare_brain
except ModuleNotFoundError:
    from lib.autonomy_depth import (
        ensure_global_policy,
        initialize_repo_depth_state,
        initialize_runtime_state,
    )
    from lib.approval_state import ApprovalStateStore
    from lib.activation_registry import ActivationRegistry
    from lib.audit_packet import build_audit_packet
    from lib.repo_preview_cache import RepoPreviewCache
    from lib.repo_profile import build_department_surfaces, build_repo_profile, write_repo_profile
    from lib.skill_inventory import refresh_repo_skill_state
    from materialize_project_claude import materialize_project_claude
    from prepare_brain import prepare_brain


SCRIPT_DIR = Path(__file__).resolve().parent


def claude_home_dir() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".claude"


def activation_registry_path() -> Path:
    return claude_home_dir() / "registry" / "activated-projects.json"


def preview_cache_path() -> Path:
    return claude_home_dir() / "registry" / "repo-previews.json"


def detect_git_root(project_dir: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(project_dir),
    )
    if result.returncode != 0:
        raise RuntimeError(f"{project_dir} is not inside a git repository")
    return Path(result.stdout.strip())


def detect_repo_name(project_dir: Path, repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(project_dir),
    )
    if result.returncode == 0:
        common_dir = Path(result.stdout.strip())
        if not common_dir.is_absolute():
            common_dir = (repo_root / common_dir).resolve()
        if common_dir.name == ".git" and common_dir.parent.name:
            return common_dir.parent.name
    return repo_root.name


def detect_stack(project_dir: Path) -> list[str]:
    checks = {
        "Python": ["pyproject.toml", "requirements.txt", "setup.py"],
        "TypeScript": ["tsconfig.json"],
        "JavaScript": ["package.json"],
        "Rust": ["Cargo.toml"],
        "Go": ["go.mod"],
        "Docker": ["Dockerfile", "docker-compose.yml"],
    }
    detected: list[str] = []
    for name, markers in checks.items():
        if any((project_dir / marker).exists() for marker in markers):
            detected.append(name)
    return detected


def detect_test_surface(project_dir: Path) -> list[str]:
    candidates = [
        project_dir / "tests",
        project_dir / "test",
        project_dir / "__tests__",
    ]
    found = [path.name for path in candidates if path.exists()]
    if (project_dir / "pytest.ini").exists():
        found.append("pytest.ini")
    return found


def detect_docs(project_dir: Path) -> list[str]:
    return [
        path.name
        for path in (project_dir / name for name in ["README.md", "ARCHITECTURE.md", "CLAUDE.md"])
        if path.exists()
    ]


def detect_package_manager(project_dir: Path) -> str:
    if (project_dir / "package-lock.json").exists():
        return "npm"
    if (project_dir / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (project_dir / "yarn.lock").exists():
        return "yarn"
    if (project_dir / "poetry.lock").exists():
        return "poetry"
    if (project_dir / "requirements.txt").exists() or (project_dir / "pyproject.toml").exists():
        return "pip"
    return "unknown"


def detect_last_commit(project_dir: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(project_dir),
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def summarize(project_dir: Path) -> dict[str, object]:
    repo_root = detect_git_root(project_dir)
    repo_name = detect_repo_name(project_dir, repo_root)
    return {
        "repo_path": str(repo_root),
        "repo_name": repo_name,
        "stack": detect_stack(repo_root),
        "docs": detect_docs(repo_root),
        "tests": detect_test_surface(repo_root),
        "package_manager": detect_package_manager(repo_root),
        "last_commit": detect_last_commit(repo_root),
        "has_brain": (repo_root / ".brain").exists(),
        "has_local_claude": (repo_root / ".claude").exists(),
        "next_state": "observe-complete",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Preview or activate an opted-in repo for the compound-brain "
            "observe/preview/prepare/activate lifecycle."
        ),
        epilog=(
            "Lifecycle:\n"
            "  1. observe     detect repo, stack, docs, tests, and current surfaces\n"
            "  2. preview     cache a read-only global recommendation\n"
            "  3. prepare     write CLAUDE.md, .brain, and .codex/AGENTS.md\n"
            "  4. activate    add repo-local .claude, departments, and runtime state"
        ),
    )
    parser.add_argument("--project-dir", default=".", help="Repo path to inspect")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run preflight only and print the detected activation state",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable preflight output",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Persist the strategic goal and departments, using provided values or recommended defaults.",
    )
    parser.add_argument(
        "--project-goal",
        help="Confirmed project goal to persist with --confirm",
    )
    parser.add_argument(
        "--departments",
        help="Comma-separated department list to persist with --confirm",
    )
    return parser


def build_preview_record(summary: dict[str, object], packet: dict[str, object]) -> dict[str, object]:
    next_actions = [
        action["title"]
        for action in packet.get("candidate_actions", [])
        if isinstance(action, dict) and "title" in action
    ]
    cache = RepoPreviewCache(preview_cache_path())
    return cache.upsert_preview(
        repo_path=str(summary["repo_path"]),
        repo_name=str(summary["repo_name"]),
        inferred_goal=str(packet["project_goal_candidates"][0]),
        departments=list(packet["departments"]),
        risks=list(packet.get("risks", [])),
        next_actions=next_actions,
        confidence=0.78,
        last_commit=str(summary["last_commit"]),
    )


def department_range_label(departments: list[str]) -> str:
    if not departments:
        return ""
    if len(departments) == 1:
        return departments[0]
    return f"{departments[0]}–{departments[-1]}"


def build_activation_recommendation(
    summary: dict[str, object],
    packet: dict[str, object],
    profile: dict[str, object],
) -> dict[str, object]:
    recommended_goal = str(profile.get("project_goal", packet["project_goal_candidates"][0]))
    detected_departments = list(profile.get("repo_native_departments", []))
    recommended_departments = detected_departments or list(packet["departments"])

    message = (
        "Before confirming goals, I'd write a proper project_goal into the approval state "
        "that reflects the repo reality"
    )
    if detected_departments:
        message += (
            f", and align the department names to the actual {department_range_label(detected_departments)} "
            "structure"
        )
    message += "."

    return {
        "message": message,
        "recommended_project_goal": recommended_goal,
        "recommended_departments": recommended_departments,
    }


def parse_departments(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def resolve_confirmation(
    args: argparse.Namespace,
    recommendation: dict[str, object],
    packet: dict[str, object],
) -> tuple[str, list[str]]:
    default_goal = str(
        args.project_goal
        or recommendation.get("recommended_project_goal")
        or packet["project_goal_candidates"][0]
    )
    default_departments = (
        parse_departments(args.departments)
        or list(recommendation.get("recommended_departments", []))
        or list(packet["departments"])
    )
    if args.confirm and sys.stdin.isatty() and not args.project_goal and not args.departments:
        entered_goal = input(f"Project goal [{default_goal}]: ").strip()
        entered_departments = input(
            f"Departments [{', '.join(default_departments)}]: "
        ).strip()
        return (
            entered_goal or default_goal,
            parse_departments(entered_departments) or default_departments,
        )
    return default_goal, default_departments


def main() -> int:
    args = build_parser().parse_args()
    try:
        summary = summarize(Path(args.project_dir).resolve())
    except RuntimeError as exc:
        print(f"[activate-repo] {exc}", file=sys.stderr)
        return 1

    packet = build_audit_packet(
        repo_name=str(summary["repo_name"]),
        tech_stack=list(summary["stack"]),
        docs_present=bool(summary["docs"]),
        ci_present=(Path(summary["repo_path"]) / ".github" / "workflows").exists(),
    )
    repo_root = Path(str(summary["repo_path"]))
    profile = build_repo_profile(
        repo_root=repo_root,
        repo_name=str(summary["repo_name"]),
        tech_stack=list(summary["stack"]),
        docs_present=bool(summary["docs"]),
        ci_present=(repo_root / ".github" / "workflows").exists(),
        default_departments=list(packet["departments"]),
        fallback_goal=str(packet["project_goal_candidates"][0]),
    )
    packet["departments"] = list(profile["departments"])
    packet["department_goals"] = {
        department: f"Improve {summary['repo_name']} through {department}-led decisions and execution"
        for department in packet["departments"]
    }
    packet["project_goal_candidates"] = [
        str(profile["project_goal"]),
        *[
            candidate
            for candidate in packet["project_goal_candidates"]
            if candidate != profile["project_goal"]
        ],
    ]
    summary["preview_record"] = build_preview_record(summary, packet)
    summary["departments"] = packet["departments"]
    summary["project_goal_candidates"] = packet["project_goal_candidates"]
    summary["recommendation"] = build_activation_recommendation(summary, packet, profile)
    summary["repo_profile"] = profile

    if args.check_only:
        summary["next_state"] = "preview-ready"
    else:
        policy = ensure_global_policy(claude_home_dir())
        if (
            not summary["has_brain"]
            or not (repo_root / "CLAUDE.md").exists()
            or not (repo_root / ".codex" / "AGENTS.md").exists()
        ):
            prepare_brain(repo_root)
        approval_store = ApprovalStateStore(repo_root / ".brain" / "state")
        if approval_store.state_path.exists():
            approval_state = approval_store.load()
        else:
            approval_state = approval_store.initialize(
                project_goal_candidates=list(packet["project_goal_candidates"]),
                departments=list(packet["departments"]),
                recommendation=dict(summary["recommendation"]),
            )

        selected_departments = list(packet["departments"])
        selected_department_goals = dict(packet["department_goals"])
        if args.confirm:
            confirmed_goal, confirmed_departments = resolve_confirmation(
                args,
                dict(summary["recommendation"]),
                packet,
            )
            selected_departments = confirmed_departments
            selected_department_goals = {
                department: f"Advance the confirmed project goal through {department}"
                for department in confirmed_departments
            }
            approval_state = approval_store.confirm_strategy(
                project_goal=confirmed_goal,
                departments=confirmed_departments,
                department_goals=selected_department_goals,
            )

        profile["department_surfaces"] = build_department_surfaces(repo_root, selected_departments)
        write_repo_profile(
            repo_root,
            {
                **profile,
                "departments": selected_departments,
                "context_files": profile["context_files"],
            },
        )
        materialize_project_claude(
            repo_root,
            selected_departments,
            department_surfaces=dict(profile["department_surfaces"]),
            department_goals=selected_department_goals,
        )
        depth_state = initialize_repo_depth_state(repo_root, policy)
        initialize_runtime_state(repo_root, depth_state)

        registry = ActivationRegistry(activation_registry_path())
        summary["registry_record"] = registry.register_repo(
            repo_path=summary["repo_path"],
            repo_name=summary["repo_name"],
            stack=list(summary["stack"]),
            activation_mode="manual",
        )
        summary["has_brain"] = True
        summary["has_local_claude"] = True
        summary["approval_state"] = approval_state["state"]
        summary["current_depth"] = depth_state["current_depth"]
        summary["skill_state"] = refresh_repo_skill_state(repo_root, claude_home=claude_home_dir())
        summary["next_state"] = "activated" if args.confirm else "awaiting-strategic-confirmation"

    if args.json:
        print(json.dumps(summary, indent=2))
        return 0

    print("compound-brain activate-repo preflight")
    print(f"repo: {summary['repo_name']} ({summary['repo_path']})")
    print(f"stack: {', '.join(summary['stack']) or 'unknown'}")
    print(f"docs: {', '.join(summary['docs']) or 'none'}")
    print(f"tests: {', '.join(summary['tests']) or 'none detected'}")
    print(f"package manager: {summary['package_manager']}")
    print(f".brain present: {'yes' if summary['has_brain'] else 'no'}")
    print(f".claude present: {'yes' if summary['has_local_claude'] else 'no'}")
    if args.check_only:
        print(f"preview goal: {summary['project_goal_candidates'][0]}")
        print(f"proposed departments: {', '.join(summary['departments'])}")
        print("recommended action: prepare-brain")
        print("next state: preview ready")
    else:
        print(f"departments: {', '.join(summary['departments'])}")
        skill_state = summary.get("skill_state", {})
        if isinstance(skill_state, dict):
            print(
                "skill state: "
                f"{len(skill_state.get('active', []))} active, "
                f"{len(skill_state.get('missing', []))} missing, "
                f"{len(skill_state.get('materialized', []))} materialized"
            )
        print(f"depth: {summary.get('current_depth', 'unknown')}")
        print("strategic confirmations: project goal, department goals, major architecture changes")
        if summary.get("approval_state") == "approved":
            state = json.loads((repo_root / ".brain" / "state" / "approval-state.json").read_text())
            print(f"project goal: {state.get('project_goal', summary['project_goal_candidates'][0])}")
            print("next state: activated")
        else:
            recommendation = summary.get("recommendation", {})
            if isinstance(recommendation, dict) and recommendation:
                print(f"Recommendation: {recommendation['message']}")
                print(
                    "  proposed project_goal: "
                    f"{recommendation.get('recommended_project_goal', summary['project_goal_candidates'][0])}"
                )
                recommended_departments = recommendation.get("recommended_departments", [])
                if recommended_departments:
                    print("  proposed departments: " + ", ".join(recommended_departments))
                print("  Want me to do that?")
            print(
                "confirm with: "
                f"python3 scripts/activate_repo.py --project-dir {repo_root} --confirm"
            )
            print("next state: awaiting strategic confirmation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
