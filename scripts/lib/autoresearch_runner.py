from __future__ import annotations

from datetime import datetime, timezone
from fnmatch import fnmatch
import json
import shutil
import re
import subprocess
from pathlib import Path
from typing import Any

try:
    from scripts.lib.autoresearch_program import load_autoresearch_program
except ModuleNotFoundError:
    from lib.autoresearch_program import load_autoresearch_program


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    return json.loads(path.read_text())


def current_commit(repo: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(repo),
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def first_hypothesis(queue_path: Path) -> str:
    if not queue_path.exists():
        return "Define the first experiment hypothesis"
    for line in queue_path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            return stripped[2:]
    return "Define the first experiment hypothesis"


def pop_first_hypothesis(queue_path: Path) -> None:
    if not queue_path.exists():
        return
    lines = queue_path.read_text().splitlines()
    remaining: list[str] = []
    removed = False
    for line in lines:
        stripped = line.strip()
        if not removed and stripped.startswith("- "):
            removed = True
            continue
        remaining.append(line)
    queue_path.write_text("\n".join(remaining).rstrip() + ("\n" if remaining else ""))


def parse_timeout_seconds(raw: str) -> int:
    match = re.search(r"(\d+)", raw)
    return int(match.group(1)) if match else 60


def extract_metric(output: str, rule: str) -> float:
    trimmed_rule = (rule or "stdout:number").strip().lower()
    if trimmed_rule.startswith("json:"):
        key = trimmed_rule.split(":", 1)[1]
        data = json.loads(output)
        value = data[key]
        return float(value)
    match = re.search(r"-?\d+(?:\.\d+)?", output)
    if not match:
        raise ValueError("unable to extract metric from evaluator output")
    return float(match.group(0))


def metric_is_better(candidate_metric: float, baseline_metric: float, keep_rule: str) -> bool:
    lowered = keep_rule.lower()
    if any(token in lowered for token in ["lower", "decrease", "smaller", "minimize"]):
        return candidate_metric < baseline_metric
    return candidate_metric > baseline_metric


def run_shell(repo: Path, command: str, timeout_seconds: int) -> tuple[int, str, str]:
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(repo),
        timeout=timeout_seconds,
    )
    return result.returncode, result.stdout, result.stderr


def run_evaluator(repo: Path, command: str, timeout_seconds: int) -> tuple[int, str, str]:
    return run_shell(repo, command, timeout_seconds)


def append_result(results_path: Path, payload: dict[str, Any]) -> None:
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with results_path.open("a") as handle:
        handle.write(json.dumps(payload) + "\n")


def lane_name() -> str:
    return "lane-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def create_experiment_lane(repo: Path, autoresearch_dir: Path) -> tuple[str, Path]:
    lane_root = autoresearch_dir / "lanes"
    lane_root.mkdir(parents=True, exist_ok=True)
    lane_path = lane_root / lane_name()
    commit = current_commit(repo)
    if commit != "unknown":
        result = subprocess.run(
            ["git", "worktree", "add", "--detach", str(lane_path), "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            cwd=str(repo),
        )
        if result.returncode == 0:
            return "worktree", lane_path
    shutil.copytree(repo, lane_path, ignore=shutil.ignore_patterns(".brain", ".git"))
    return "copy", lane_path


def cleanup_experiment_lane(repo: Path, lane_kind: str, lane_path: Path) -> None:
    if lane_kind == "worktree":
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(lane_path)],
            capture_output=True,
            text=True,
            check=False,
            cwd=str(repo),
        )
    if lane_path.exists():
        shutil.rmtree(lane_path, ignore_errors=True)


def parse_status_line(line: str) -> tuple[str, str]:
    status = line[:2].strip()
    path = line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return status, path


def detect_changed_files(lane_path: Path) -> tuple[list[str], list[str]]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(lane_path),
    )
    if result.returncode != 0:
        return [], []
    changed: list[str] = []
    deleted: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        status, path = parse_status_line(line)
        if "D" in status:
            deleted.append(path)
        else:
            changed.append(path)
    return sorted(dict.fromkeys(changed)), sorted(dict.fromkeys(deleted))


def path_allowed(path: str, patterns: list[str]) -> bool:
    if not patterns:
        return True
    return any(
        fnmatch(path, pattern)
        or path == pattern
        or path.startswith(pattern.rstrip("/") + "/")
        for pattern in patterns
    )


def apply_lane_back_to_repo(
    repo: Path,
    lane_path: Path,
    changed_files: list[str],
    deleted_files: list[str],
) -> None:
    for rel_path in changed_files:
        source = lane_path / rel_path
        target = repo / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for rel_path in deleted_files:
        target = repo / rel_path
        if target.exists():
            target.unlink()


def run_mutation_cycle(
    repo: Path,
    autoresearch_dir: Path,
    *,
    department: str,
    hypothesis: str,
    baseline_metric: float,
    program: dict[str, Any],
    timeout_seconds: int,
) -> dict[str, Any]:
    lane_kind, lane_path = create_experiment_lane(repo, autoresearch_dir)
    mutation_command = str(program.get("mutation_command", "")).strip()
    results_path = autoresearch_dir / "results.jsonl"
    try:
        mutation_rc, mutation_stdout, mutation_stderr = run_shell(lane_path, mutation_command, timeout_seconds)
        if mutation_rc != 0:
            result = {
                "timestamp": now_utc(),
                "department": department,
                "status": "failed",
                "reason": "mutation-command-failed",
                "hypothesis": hypothesis,
                "objective": program.get("objective", ""),
                "commit": current_commit(repo),
                "lane": lane_kind,
                "stdout": mutation_stdout[-400:],
                "stderr": mutation_stderr[-400:],
            }
            append_result(results_path, result)
            return result

        changed_files, deleted_files = detect_changed_files(lane_path)
        mutable_surfaces = list(program.get("mutable_surfaces", []))
        protected_surfaces = list(program.get("protected_surfaces", []))
        all_changes = [*changed_files, *deleted_files]
        invalid_changes = [
            item
            for item in all_changes
            if not path_allowed(item, mutable_surfaces)
            or (protected_surfaces and path_allowed(item, protected_surfaces))
        ]
        if invalid_changes:
            result = {
                "timestamp": now_utc(),
                "department": department,
                "status": "blocked",
                "reason": "mutation-outside-mutable-surfaces",
                "hypothesis": hypothesis,
                "objective": program.get("objective", ""),
                "commit": current_commit(repo),
                "lane": lane_kind,
                "changed_files": all_changes,
                "invalid_changes": invalid_changes,
            }
            append_result(results_path, result)
            return result

        rc, stdout, stderr = run_evaluator(lane_path, str(program.get("run_command", "")), timeout_seconds)
        if rc != 0:
            result = {
                "timestamp": now_utc(),
                "department": department,
                "status": "failed",
                "reason": "evaluator-failed",
                "hypothesis": hypothesis,
                "objective": program.get("objective", ""),
                "commit": current_commit(repo),
                "lane": lane_kind,
                "changed_files": changed_files,
                "stdout": stdout[-400:],
                "stderr": stderr[-400:],
            }
            append_result(results_path, result)
            return result

        candidate_metric = extract_metric(stdout, str(program.get("metric_extraction_rule", "")))
        keep = metric_is_better(candidate_metric, baseline_metric, str(program.get("keep_discard_rule", "")))
        if keep:
            apply_lane_back_to_repo(repo, lane_path, changed_files, deleted_files)

        result = {
            "timestamp": now_utc(),
            "department": department,
            "status": "kept" if keep else "discarded",
            "reason": "metric-improved" if keep else "metric-not-better",
            "hypothesis": hypothesis,
            "objective": program.get("objective", ""),
            "commit": current_commit(repo),
            "baseline_metric": baseline_metric,
            "candidate_metric": candidate_metric,
            "lane": lane_kind,
            "changed_files": changed_files,
            "deleted_files": deleted_files,
            "evaluator_stdout": stdout[-400:],
            "evaluator_stderr": stderr[-400:],
        }
        append_result(results_path, result)
        return result
    finally:
        cleanup_experiment_lane(repo, lane_kind, lane_path)


def run_autoresearch_cycle(repo: Path, department: str) -> dict[str, Any]:
    repo = repo.resolve()
    approval = load_json(
        repo / ".brain" / "state" / "approval-state.json",
        {"state": "inactive", "pending": []},
    )
    if "autoresearch_enable" in approval.get("pending", []):
        return {
            "department": department,
            "status": "blocked",
            "reason": "autoresearch-not-approved",
        }

    autoresearch_dir = repo / ".brain" / "autoresearch"
    program_path = autoresearch_dir / "program.md"
    if not program_path.exists():
        return {
            "department": department,
            "status": "blocked",
            "reason": "missing-program",
        }

    program = load_autoresearch_program(program_path)
    run_command = str(program.get("run_command", "")).strip()
    if not run_command:
        return {
            "department": department,
            "status": "blocked",
            "reason": "missing-run-command",
        }

    timeout_seconds = parse_timeout_seconds(str(program.get("runtime_budget", "")))
    baseline_path = autoresearch_dir / "baseline.json"
    results_path = autoresearch_dir / "results.jsonl"
    if not baseline_path.exists():
        rc, stdout, stderr = run_evaluator(repo, run_command, timeout_seconds)
        if rc != 0:
            result = {
                "timestamp": now_utc(),
                "department": department,
                "status": "failed",
                "reason": "baseline-evaluator-failed",
                "objective": program.get("objective", ""),
                "commit": current_commit(repo),
                "stdout": stdout[-400:],
                "stderr": stderr[-400:],
            }
            append_result(results_path, result)
            return result

        metric = extract_metric(stdout, str(program.get("metric_extraction_rule", "")))
        baseline = {
            "baseline_commit": current_commit(repo),
            "baseline_metric": metric,
            "timestamp": now_utc(),
            "evaluator_version": program.get("fixed_evaluator", ""),
        }
        baseline_path.write_text(json.dumps(baseline, indent=2) + "\n")
        result = {
            "timestamp": now_utc(),
            "department": department,
            "status": "baseline-recorded",
            "reason": "baseline-created",
            "objective": program.get("objective", ""),
            "commit": current_commit(repo),
            "metric": metric,
        }
        append_result(results_path, result)
        return result

    baseline = load_json(baseline_path, {})
    hypothesis = first_hypothesis(autoresearch_dir / "queue.md")
    baseline_metric = float(baseline.get("baseline_metric", 0.0))

    if str(program.get("mutation_command", "")).strip():
        result = run_mutation_cycle(
            repo,
            autoresearch_dir,
            department=department,
            hypothesis=hypothesis,
            baseline_metric=baseline_metric,
            program=program,
            timeout_seconds=timeout_seconds,
        )
    else:
        rc, stdout, stderr = run_evaluator(repo, run_command, timeout_seconds)
        if rc != 0:
            result = {
                "timestamp": now_utc(),
                "department": department,
                "status": "failed",
                "reason": "evaluator-failed",
                "hypothesis": hypothesis,
                "objective": program.get("objective", ""),
                "commit": current_commit(repo),
                "stdout": stdout[-400:],
                "stderr": stderr[-400:],
            }
            append_result(results_path, result)
            return result
        candidate_metric = extract_metric(stdout, str(program.get("metric_extraction_rule", "")))
        keep = metric_is_better(candidate_metric, baseline_metric, str(program.get("keep_discard_rule", "")))
        result = {
            "timestamp": now_utc(),
            "department": department,
            "status": "kept" if keep else "discarded",
            "reason": "metric-improved" if keep else "metric-not-better",
            "hypothesis": hypothesis,
            "objective": program.get("objective", ""),
            "commit": current_commit(repo),
            "baseline_metric": baseline_metric,
            "candidate_metric": candidate_metric,
            "evaluator_stdout": stdout[-400:],
            "evaluator_stderr": stderr[-400:],
        }
        append_result(results_path, result)

    if result.get("status") == "kept":
        baseline.update(
            {
                "baseline_commit": current_commit(repo),
                "baseline_metric": result.get("candidate_metric", baseline_metric),
                "timestamp": now_utc(),
                "evaluator_version": program.get("fixed_evaluator", ""),
                "last_lane": result.get("lane", "repo"),
                "last_changed_files": result.get("changed_files", []),
            }
        )
        baseline_path.write_text(json.dumps(baseline, indent=2) + "\n")
        pop_first_hypothesis(autoresearch_dir / "queue.md")
    return result
