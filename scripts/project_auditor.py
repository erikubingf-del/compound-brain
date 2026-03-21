#!/usr/bin/env python3
"""
project_auditor.py — Initial deep audit of a project when added to compound-brain.

Runs once (or on-demand) to:
1. Map the codebase structure and tech stack
2. Understand architecture, dependencies, and patterns
3. Read all CLAUDE.md / README / planning files
4. Identify open issues, risks, and improvement opportunities
5. Score project health across 6 dimensions
6. Write comprehensive audit report to .brain/knowledge/

Then sets up the probability engine baseline and agent layer registry.

Usage:
    python3 project_auditor.py --project-dir /path/to/project
    python3 project_auditor.py --all-registered              # audit all projects
    python3 project_auditor.py --project-dir /path --force   # re-audit existing
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CLAUDE_BIN = "__CLAUDE_BIN__"
CONFIG_FILE = Path.home() / ".claude" / "intelligence_projects.json"

AUDIT_DIMENSIONS = [
    "code_quality",       # Test coverage, lint, complexity
    "documentation",      # README, CLAUDE.md, inline docs
    "architecture",       # Structure, separation of concerns, patterns
    "security",           # Known vulnerabilities, secrets handling
    "performance",        # Known bottlenecks, inefficiencies
    "momentum",           # Activity level, issue resolution speed
]


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def date_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def read_safe(path: Path, max_chars: int = 3000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""


# ─── Collectors ──────────────────────────────────────────────────────────────

def collect_project_data(project_dir: Path) -> dict:
    """Gather all available project data for the audit prompt."""
    d = {}

    # Identity
    d["name"] = project_dir.name
    d["claude_md"] = read_safe(project_dir / "CLAUDE.md", 2000)
    d["readme"] = read_safe(project_dir / "README.md", 1500)

    # Git
    d["git_log"] = _run(["git", "log", "--oneline", "-20", "--no-decorate"], project_dir)
    d["git_contributors"] = _run(["git", "shortlog", "-sn", "--no-merges", "-10"], project_dir)
    d["git_diff_stat"] = _run(["git", "diff", "--stat", "HEAD~5", "HEAD"], project_dir)

    # Structure
    d["top_files"] = _list_top_files(project_dir)
    d["tech_stack"] = _detect_tech_stack(project_dir)
    d["test_files"] = _find_test_files(project_dir)
    d["config_files"] = _find_config_files(project_dir)

    # Planning
    d["planning_state"] = read_safe(project_dir / ".planning" / "STATE.md", 1000)
    d["planning_roadmap"] = read_safe(project_dir / ".planning" / "ROADMAP.md", 1000)

    # Existing brain
    d["brain_memory"] = _read_brain_memory(project_dir)
    d["brain_decisions"] = read_safe(
        project_dir / ".brain" / "knowledge" / "decisions" / "log.md", 800
    )

    # Issues
    d["todo_count"] = _count_todos(project_dir)

    return d


def _run(cmd: list, cwd: Path, timeout: int = 10) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(cwd))
        return r.stdout.strip()[:1500]
    except Exception:
        return ""


def _list_top_files(project_dir: Path) -> str:
    try:
        items = sorted(project_dir.iterdir())
        names = [
            f.name for f in items
            if not f.name.startswith(".")
            and f.name not in {"node_modules", "__pycache__", "venv", ".git", "dist", "build"}
        ]
        return ", ".join(names[:25])
    except Exception:
        return ""


def _detect_tech_stack(project_dir: Path) -> list[str]:
    stack = []
    checks = {
        "Python": ["*.py", "pyproject.toml", "setup.py", "requirements.txt"],
        "TypeScript": ["*.ts", "tsconfig.json"],
        "JavaScript": ["*.js", "package.json"],
        "React": ["src/App.tsx", "src/App.jsx"],
        "Next.js": ["next.config.js", "next.config.ts"],
        "Rust": ["Cargo.toml"],
        "Go": ["go.mod"],
        "Docker": ["Dockerfile", "docker-compose.yml"],
        "Terraform": ["*.tf"],
        "GitHub Actions": [".github/workflows"],
    }
    for tech, patterns in checks.items():
        for p in patterns:
            if "*" in p:
                if any(project_dir.rglob(p)):
                    stack.append(tech)
                    break
            else:
                if (project_dir / p).exists():
                    stack.append(tech)
                    break
    return stack


def _find_test_files(project_dir: Path) -> str:
    test_dirs = ["tests", "test", "__tests__", "spec"]
    found = []
    for td in test_dirs:
        path = project_dir / td
        if path.exists():
            count = sum(1 for _ in path.rglob("*.py")) + sum(1 for _ in path.rglob("*.ts")) + sum(1 for _ in path.rglob("*.js"))
            found.append(f"{td}/ ({count} files)")
    return ", ".join(found) if found else "No test directory found"


def _find_config_files(project_dir: Path) -> str:
    configs = []
    for name in [".env.example", "config.yml", "config.yaml", "config.json", "pyproject.toml",
                 "package.json", "Makefile", "justfile", ".eslintrc*", "jest.config*"]:
        if any(project_dir.glob(name)):
            configs.append(name.rstrip("*"))
    return ", ".join(configs) if configs else "none found"


def _read_brain_memory(project_dir: Path) -> str:
    brain_mem = project_dir / ".brain" / "memory"
    if not brain_mem.exists():
        return "No .brain/memory/ yet"
    parts = []
    for f in sorted(brain_mem.glob("*.md"))[:4]:
        content = read_safe(f, 400)
        if content:
            parts.append(f"[{f.name}]\n{content}")
    return "\n".join(parts) or "Empty"


def _count_todos(project_dir: Path) -> int:
    try:
        r = subprocess.run(
            ["grep", "-r", "--include=*.py", "--include=*.ts", "--include=*.js",
             "-c", r"TODO\|FIXME"],
            capture_output=True, text=True, timeout=10, cwd=str(project_dir)
        )
        return sum(int(l.split(":")[-1]) for l in r.stdout.strip().split("\n") if ":" in l and l.split(":")[-1].isdigit())
    except Exception:
        return 0


# ─── LLM audit ───────────────────────────────────────────────────────────────

def compose_audit_prompt(data: dict) -> str:
    return f"""You are the compound-brain project auditor. Perform a comprehensive audit of project "{data['name']}".

## Project Identity
CLAUDE.md excerpt:
{data['claude_md'][:800] or 'Not found'}

README excerpt:
{data['readme'][:600] or 'Not found'}

## Tech Stack
{', '.join(data['tech_stack']) if data['tech_stack'] else 'Unknown'}

## Structure
Top-level: {data['top_files']}
Config files: {data['config_files']}
Tests: {data['test_files']}
TODO count: {data['todo_count']}

## Git History (last 20 commits)
{data['git_log'] or 'No git history'}

## Planning State
{data['planning_state'] or data['planning_roadmap'] or 'No planning files'}

## Existing Memory
{data['brain_memory']}

---
Generate a comprehensive audit report with these sections:

### 1. PROJECT SUMMARY (3 sentences)
What this project does, its current state, and primary goal.

### 2. HEALTH SCORES (score each 1-10 with 1-sentence rationale)
- code_quality: /10 — [rationale]
- documentation: /10 — [rationale]
- architecture: /10 — [rationale]
- security: /10 — [rationale]
- performance: /10 — [rationale]
- momentum: /10 — [rationale]
- OVERALL: /10

### 3. ARCHITECTURE ANALYSIS (5 bullets)
Key architectural patterns, what works well, what has risk.

### 4. TOP 5 IMPROVEMENT OPPORTUNITIES
Ranked by impact × feasibility. For each: what, why, estimated effort (S/M/L).

### 5. RISKS (3 bullets)
What could cause the project to fail or stall.

### 6. AGENT LAYER RECOMMENDATIONS
Which autonomous agent programs should run for this project:
- discovery_loop: yes/no — [why]
- monitor_loop: yes/no — [why]
- architecture_guardian: yes/no — [why]
- github_intel: yes/no — [why]

### 7. NEXT SESSION ACTION
Single most important thing to do in the next session.

Be specific. Reference actual files and patterns found. Max 600 words."""


def call_claude(prompt: str) -> str:
    try:
        result = subprocess.run(
            [CLAUDE_BIN, "--dangerously-skip-permissions", "--print", "-p", prompt],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return f"[audit failed: claude error rc={result.returncode}]"
    except subprocess.TimeoutExpired:
        return "[audit timed out after 120s]"
    except FileNotFoundError:
        return f"[claude not found at {CLAUDE_BIN}]"
    except Exception as e:
        return f"[audit failed: {e}]"


# ─── Output ───────────────────────────────────────────────────────────────────

def write_audit(project_dir: Path, project_name: str, audit: str, data: dict) -> Path:
    """Write audit report to .brain/knowledge/ and latest snapshot."""
    brain_dir = project_dir / ".brain" / "knowledge"
    brain_dir.mkdir(parents=True, exist_ok=True)

    d = date_str()
    audit_dir = brain_dir / "areas"
    audit_dir.mkdir(exist_ok=True)

    # Full audit report
    report_path = audit_dir / "project-audit.md"
    ts = now_utc()
    content = f"""---
title: Project Audit — {project_name}
updated: {d}
---

# Project Audit — {project_name}
*Generated: {ts} by compound-brain project_auditor*

{audit}

---
## Raw Data Snapshot

**Tech stack detected:** {', '.join(data['tech_stack'])}
**TODO markers:** {data['todo_count']}
**Test files:** {data['test_files']}
"""
    report_path.write_text(content)

    # Also write JSON health snapshot for probability engine
    health_path = brain_dir / "areas" / "health-snapshot.json"
    try:
        health = {"timestamp": ts, "project": project_name, "tech_stack": data["tech_stack"], "todo_count": data["todo_count"]}
        # Extract scores from audit text
        for dim in AUDIT_DIMENSIONS:
            for line in audit.split("\n"):
                if dim in line.lower() and "/10" in line:
                    try:
                        score_part = line.split("/10")[0]
                        score = float(score_part.split()[-1])
                        health[f"score_{dim}"] = score
                        break
                    except Exception:
                        pass
        health_path.write_text(json.dumps(health, indent=2))
    except Exception:
        pass

    return report_path


# ─── Main ────────────────────────────────────────────────────────────────────

def audit_project(project_dir: Path, force: bool = False) -> bool:
    """Run audit for a single project. Returns True if audit was performed."""
    audit_path = project_dir / ".brain" / "knowledge" / "areas" / "project-audit.md"

    if audit_path.exists() and not force:
        # Check age — re-audit if older than 30 days
        import time
        age_days = (time.time() - audit_path.stat().st_mtime) / 86400
        if age_days < 30:
            print(f"  [skip] {project_dir.name}: audit is {age_days:.0f} days old (use --force to re-audit)")
            return False

    print(f"\n[auditor] Auditing: {project_dir.name}")
    print(f"  Collecting project data...")
    data = collect_project_data(project_dir)

    print(f"  Tech stack: {', '.join(data['tech_stack']) or 'unknown'}")
    print(f"  Calling claude for deep audit (~60s)...")

    prompt = compose_audit_prompt(data)
    audit = call_claude(prompt)

    report_path = write_audit(project_dir, project_dir.name, audit, data)
    print(f"  Audit written → {report_path}")

    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="compound-brain project auditor")
    parser.add_argument("--project-dir", help="Path to single project")
    parser.add_argument("--all-registered", action="store_true", help="Audit all registered projects")
    parser.add_argument("--force", action="store_true", help="Re-audit even if recent audit exists")
    args = parser.parse_args()

    print(f"[auditor] Starting {now_utc()}")

    if args.all_registered:
        config = json.loads(CONFIG_FILE.read_text()) if CONFIG_FILE.exists() else {}
        projects = [Path(p["path"]) for p in config.get("projects", []) if p.get("enabled", True)]
        if not projects:
            print("[auditor] No registered projects found")
            sys.exit(0)
        for p in projects:
            if p.exists():
                audit_project(p, force=args.force)
    elif args.project_dir:
        project_dir = Path(args.project_dir).resolve()
        if not project_dir.exists():
            print(f"ERROR: {project_dir} does not exist")
            sys.exit(1)
        audit_project(project_dir, force=args.force)
    else:
        parser.print_help()

    print(f"\n[auditor] Done. {now_utc()}")


if __name__ == "__main__":
    main()
