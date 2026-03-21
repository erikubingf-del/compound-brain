#!/usr/bin/env python3
"""activate_repo.py — preflight and registration entry point for alive repos."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    from scripts.lib.activation_registry import ActivationRegistry
except ModuleNotFoundError:
    from lib.activation_registry import ActivationRegistry


REGISTRY_PATH = Path.home() / ".claude" / "registry" / "activated-projects.json"


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
        "has_brain": (repo_root / ".brain").exists(),
        "has_local_claude": (repo_root / ".claude").exists(),
        "next_state": "preflight-complete",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Activate an opted-in repo: run preflight, detect surfaces, and "
            "register it for the compound-brain activation lifecycle."
        )
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


def main() -> int:
    args = build_parser().parse_args()
    try:
        summary = summarize(Path(args.project_dir).resolve())
    except RuntimeError as exc:
        print(f"[activate-repo] {exc}", file=sys.stderr)
        return 1

    if not args.check_only:
        registry = ActivationRegistry(REGISTRY_PATH)
        summary["registry_record"] = registry.register_repo(
            repo_path=summary["repo_path"],
            repo_name=summary["repo_name"],
            stack=list(summary["stack"]),
            activation_mode="manual",
        )
        summary["next_state"] = "registered"

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
        print("next state: preflight complete")
    else:
        print("next state: registered for activation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
