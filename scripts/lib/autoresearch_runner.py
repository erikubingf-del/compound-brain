from __future__ import annotations

from datetime import datetime, timezone
import json
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
        return default
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


def run_evaluator(repo: Path, command: str, timeout_seconds: int) -> tuple[int, str, str]:
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(repo),
        timeout=timeout_seconds,
    )
    return (result.returncode, result.stdout, result.stderr)


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
            with (autoresearch_dir / "results.jsonl").open("a") as handle:
                handle.write(json.dumps(result) + "\n")
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
        with (autoresearch_dir / "results.jsonl").open("a") as handle:
            handle.write(json.dumps(result) + "\n")
        return result

    baseline = load_json(baseline_path, {})
    hypothesis = first_hypothesis(autoresearch_dir / "queue.md")
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
        with (autoresearch_dir / "results.jsonl").open("a") as handle:
            handle.write(json.dumps(result) + "\n")
        return result

    candidate_metric = extract_metric(stdout, str(program.get("metric_extraction_rule", "")))
    baseline_metric = float(baseline.get("baseline_metric", candidate_metric))
    keep = metric_is_better(candidate_metric, baseline_metric, str(program.get("keep_discard_rule", "")))
    if keep:
        baseline.update(
            {
                "baseline_commit": current_commit(repo),
                "baseline_metric": candidate_metric,
                "timestamp": now_utc(),
                "evaluator_version": program.get("fixed_evaluator", ""),
            }
        )
        baseline_path.write_text(json.dumps(baseline, indent=2) + "\n")
        pop_first_hypothesis(autoresearch_dir / "queue.md")

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
    with (autoresearch_dir / "results.jsonl").open("a") as handle:
        handle.write(json.dumps(result) + "\n")
    return result
