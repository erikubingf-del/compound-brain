#!/usr/bin/env python3
"""Run self-hosting architecture checks and update the compound-brain scorecard."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

try:
    from scripts.lib.architecture_evaluator import (
        build_architecture_scorecard,
        load_architecture_evaluator,
        write_architecture_scorecard,
    )
except ModuleNotFoundError:
    from lib.architecture_evaluator import (
        build_architecture_scorecard,
        load_architecture_evaluator,
        write_architecture_scorecard,
    )


def run_check(command: list[str], cwd: Path) -> bool:
    result = subprocess.run(command, capture_output=True, text=True, check=False, cwd=str(cwd))
    return result.returncode == 0


def activation_smoke(repo_root: Path) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "demo"
        repo.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init"], capture_output=True, text=True, check=False, cwd=str(repo))
        check = run_check(
            ["python3", str(repo_root / "scripts" / "activate_repo.py"), "--project-dir", str(repo), "--check-only"],
            cwd=repo_root,
        )
        prepare = run_check(
            ["python3", str(repo_root / "scripts" / "prepare_brain.py"), str(repo)],
            cwd=repo_root,
        )
        activate = run_check(
            ["python3", str(repo_root / "scripts" / "activate_repo.py"), "--project-dir", str(repo)],
            cwd=repo_root,
        )
        return check and prepare and activate


def rubric_results(repo_root: Path) -> dict[str, str]:
    required_sets = {
        "Control-plane integrity": [
            repo_root / "scripts" / "activate_repo.py",
            repo_root / "scripts" / "prepare_brain.py",
            repo_root / "templates" / "project_claude" / "settings.local.json",
        ],
        "Claude/Codex parity": [
            repo_root / "scripts" / "bootstrap_codex_runtime.py",
            repo_root / "templates" / "project_codex" / "AGENTS.md",
        ],
        "Approval safety": [
            repo_root / "scripts" / "lib" / "approval_state.py",
            repo_root / "scripts" / "activate_repo.py",
        ],
        "Upgradeability": [
            repo_root / "install.sh",
            repo_root / "scripts" / "materialize_project_claude.py",
        ],
        "Autonomy boundedness": [
            repo_root / "scripts" / "lib" / "department_cycle.py",
            repo_root / "scripts" / "lib" / "autoresearch_runner.py",
        ],
        "Observability and log quality": [
            repo_root / "scripts" / "project_intelligence.py",
            repo_root / "scripts" / "review_promotion_inbox.py",
            repo_root / "scripts" / "global_intelligence_sweeper.py",
        ],
    }
    return {
        label: ("pass" if all(path.exists() for path in paths) else "fail")
        for label, paths in required_sets.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Update compound-brain self-hosting architecture scorecard.")
    parser.add_argument("--repo-root", default=str(Path.cwd()), help="Repository root")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    evaluator_path = repo_root / ".brain" / "architecture" / "evaluator.md"
    scorecard_path = repo_root / ".brain" / "architecture" / "scorecard.json"
    evaluator = load_architecture_evaluator(evaluator_path)
    previous = json.loads(scorecard_path.read_text()) if scorecard_path.exists() else {}

    gate_names = list(evaluator.get("deterministic_gates", []))
    deterministic_gate_results: dict[str, bool] = {}
    if gate_names:
        deterministic_gate_results[gate_names[0]] = run_check(
            ["python3", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
            cwd=repo_root,
        )
    if len(gate_names) > 1:
        deterministic_gate_results[gate_names[1]] = run_check(["bash", "install.sh", "--dry-run"], cwd=repo_root)
    if len(gate_names) > 2:
        deterministic_gate_results[gate_names[2]] = activation_smoke(repo_root)
    current_rubric = rubric_results(repo_root)
    canary_behavior = "pass" if activation_smoke(repo_root) else "regressed"

    scorecard = build_architecture_scorecard(
        previous=previous,
        deterministic_gate_results=deterministic_gate_results,
        rubric_results=current_rubric,
        canary_behavior=canary_behavior,
    )
    write_architecture_scorecard(scorecard_path, scorecard)
    print(f"compound-brain architecture scorecard updated: {scorecard['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
