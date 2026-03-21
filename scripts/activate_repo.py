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
    from scripts.lib.activation_registry import ActivationRegistry
    from scripts.lib.audit_packet import build_audit_packet
    from scripts.lib.repo_preview_cache import RepoPreviewCache
    from scripts.materialize_project_claude import materialize_project_claude
except ModuleNotFoundError:
    from lib.activation_registry import ActivationRegistry
    from lib.audit_packet import build_audit_packet
    from lib.repo_preview_cache import RepoPreviewCache
    from materialize_project_claude import materialize_project_claude


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
        if common_dir.name == ".git":
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
    return parser


def ensure_brain(repo_root: Path, repo_name: str) -> None:
    setup_script = SCRIPT_DIR / "setup_brain.sh"
    subprocess.run(
        ["bash", str(setup_script), str(repo_root), repo_name],
        capture_output=True,
        text=True,
        check=True,
    )


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
    summary["preview_record"] = build_preview_record(summary, packet)
    summary["departments"] = packet["departments"]
    summary["project_goal_candidates"] = packet["project_goal_candidates"]

    if args.check_only:
        summary["next_state"] = "preview-ready"
    else:
        repo_root = Path(summary["repo_path"])
        if not summary["has_brain"]:
            ensure_brain(repo_root, str(summary["repo_name"]))
        materialize_project_claude(repo_root, list(packet["departments"]))

        registry = ActivationRegistry(activation_registry_path())
        summary["registry_record"] = registry.register_repo(
            repo_path=summary["repo_path"],
            repo_name=summary["repo_name"],
            stack=list(summary["stack"]),
            activation_mode="manual",
        )
        summary["has_brain"] = True
        summary["has_local_claude"] = True
        summary["next_state"] = "awaiting-strategic-confirmation"

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
        print("strategic confirmations: project goal, department goals, major architecture changes")
        print("next state: awaiting strategic confirmation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
