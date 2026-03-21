#!/usr/bin/env python3
"""
global_intelligence_sweeper.py — Multi-project LLM intelligence sweep.

Runs every 6h via crontab. For each registered project:
  1. Runs project_intelligence.py to generate per-project brief
  2. Collects briefs into a global cross-project summary
  3. Writes global summary to ~/.claude/knowledge/daily/YYYY-MM-DD.md

Auto-discovers projects from:
  - ~/.claude/intelligence_projects.json (manually curated list)
  - ~/Documents/GitHub/*/CLAUDE.md (auto-detected)

Usage:
    python3 global_intelligence_sweeper.py
    python3 global_intelligence_sweeper.py --dry-run
    python3 global_intelligence_sweeper.py --list      # show registered projects
    python3 global_intelligence_sweeper.py --register /path/to/project  # add project
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CLAUDE_BIN = "__CLAUDE_BIN__"
PROJECT_INTEL_SCRIPT = Path(__file__).parent / "project_intelligence.py"
GLOBAL_KNOWLEDGE = Path.home() / ".claude" / "knowledge"
CONFIG_FILE = Path.home() / ".claude" / "intelligence_projects.json"
GITHUB_DIR = Path.home() / "Documents" / "GitHub"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def date_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ─── Project registry ────────────────────────────────────────────────────────

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    return {"projects": [], "auto_discover": True, "max_projects_per_run": 5}


def save_config(config: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def discover_projects() -> list[Path]:
    """Find all projects with CLAUDE.md in GitHub dir."""
    projects = []
    if GITHUB_DIR.exists():
        for d in sorted(GITHUB_DIR.iterdir()):
            if d.is_dir() and (d / "CLAUDE.md").exists() and (d / ".git").exists():
                projects.append(d)
    return projects


def get_active_projects(config: dict) -> list[Path]:
    """Get list of projects to process this run."""
    # Explicitly registered projects
    registered = [Path(p["path"]) for p in config.get("projects", []) if p.get("enabled", True)]

    # Auto-discovered if enabled
    if config.get("auto_discover", True):
        discovered = discover_projects()
        # Merge: registered first, then discovered (deduplicated)
        seen = {str(p) for p in registered}
        for d in discovered:
            if str(d) not in seen:
                registered.append(d)
                seen.add(str(d))

    # Filter to existing dirs
    active = [p for p in registered if p.exists()]

    # Limit per run to avoid timeout
    max_n = config.get("max_projects_per_run", 5)
    return active[:max_n]


# ─── Per-project runner ──────────────────────────────────────────────────────

def run_project_intelligence(project_dir: Path, dry_run: bool = False) -> str | None:
    """Run project_intelligence.py for a single project, return analysis."""
    try:
        cmd = [sys.executable, str(PROJECT_INTEL_SCRIPT), "--project-dir", str(project_dir)]
        if dry_run:
            cmd.append("--dry-run")

        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
            cwd=str(project_dir)
        )

        # Read brief from latest file
        brief_path = project_dir / ".brain" / "knowledge" / "daily" / "intelligence_brief_latest.md"
        if brief_path.exists():
            mtime = brief_path.stat().st_mtime
            age_s = datetime.now(timezone.utc).timestamp() - mtime
            if age_s < 300:  # written in last 5 min = fresh
                return brief_path.read_text(encoding="utf-8", errors="replace").strip()

        # Fallback: use stdout
        return result.stdout.strip() or None

    except subprocess.TimeoutExpired:
        return f"[{project_dir.name}] timed out"
    except Exception as e:
        return f"[{project_dir.name}] failed: {e}"


# ─── Global summary ──────────────────────────────────────────────────────────

def compose_global_prompt(project_briefs: dict[str, str]) -> str:
    ts = now_utc()
    briefs_text = ""
    for name, brief in project_briefs.items():
        briefs_text += f"\n### {name}\n{brief[:400]}\n"

    return f"""You are the cross-project intelligence analyst for all of Erik's projects.
Synthesize the individual project briefs into a global strategic summary for {ts}.

## Individual Project Briefs
{briefs_text}

---
Generate a global summary:

**PORTFOLIO STATUS** (2 lines): Overall health across all projects.

**CROSS-PROJECT PATTERNS** (2-3 bullets): What themes, risks, or opportunities appear across multiple projects?

**HIGHEST PRIORITY PROJECT** (1 bullet): Which project needs attention most urgently and why?

**GLOBAL IMPROVEMENT OPPORTUNITY** (1-2 bullets): What systemic improvement would benefit multiple projects?

**STALE / AT-RISK PROJECTS** (list): Projects showing no recent activity or accumulating debt.

Rules: max 200 words, bullet points, no preamble."""


def call_claude(prompt: str) -> str:
    try:
        result = subprocess.run(
            [CLAUDE_BIN, "--dangerously-skip-permissions", "--print", "-p", prompt],
            capture_output=True, text=True, timeout=90,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return f"[claude error]: {result.stderr[:200]}"
    except Exception as e:
        return f"[claude failed: {e}]"


def write_global_summary(summary: str, project_briefs: dict[str, str]) -> None:
    ts = now_utc()
    d = date_str()

    daily_dir = GLOBAL_KNOWLEDGE / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)

    daily_path = daily_dir / f"{d}.md"
    latest_path = daily_dir / "intelligence_sweep_latest.md"

    section = f"\n\n## Global Intelligence Sweep [{ts}]\n\n{summary}\n\n"
    section += "### Individual Briefs Summary\n"
    for name, brief in project_briefs.items():
        first_line = brief.split("\n")[0] if brief else "No analysis"
        section += f"- **{name}**: {first_line[:100]}\n"

    if daily_path.exists():
        with open(daily_path, "a") as f:
            f.write(section)
    else:
        with open(daily_path, "w") as f:
            f.write(f"# Global Daily Notes — {d}{section}")

    latest_path.write_text(f"# Global Intelligence Sweep — {ts}\n\n{summary}\n")

    print(f"\n[sweeper] Global summary → {daily_path}")
    print(f"[sweeper] Latest snapshot → {latest_path}")


# ─── Main ────────────────────────────────────────────────────────────────────

def cmd_list() -> None:
    config = load_config()
    projects = get_active_projects(config)
    print(f"Registered projects ({len(projects)}):")
    for p in projects:
        has_brain = "🧠" if (p / ".brain").exists() else "  "
        has_plan = "📋" if (p / ".planning").exists() else "  "
        print(f"  {has_brain}{has_plan} {p.name:30s} {p}")


def cmd_register(project_path: str) -> None:
    config = load_config()
    path = Path(project_path).resolve()
    if not path.exists():
        print(f"ERROR: {path} does not exist")
        sys.exit(1)

    projects = config.setdefault("projects", [])
    existing = [p["path"] for p in projects]
    if str(path) in existing:
        print(f"Already registered: {path}")
        return

    projects.append({"path": str(path), "name": path.name, "enabled": True})
    save_config(config)
    print(f"Registered: {path.name} ({path})")


def cmd_sweep(dry_run: bool = False) -> None:
    print(f"[sweeper] Starting global intelligence sweep {now_utc()}")
    config = load_config()
    projects = get_active_projects(config)

    if not projects:
        print("[sweeper] No projects found. Run with --list to check discovery.")
        return

    print(f"[sweeper] Processing {len(projects)} projects...")

    project_briefs: dict[str, str] = {}
    for project_dir in projects:
        print(f"\n[sweeper] → {project_dir.name}")
        brief = run_project_intelligence(project_dir, dry_run=dry_run)
        if brief:
            project_briefs[project_dir.name] = brief

    if not project_briefs:
        print("[sweeper] No briefs collected.")
        return

    if not dry_run:
        print("\n[sweeper] Generating global summary...")
        global_prompt = compose_global_prompt(project_briefs)
        global_summary = call_claude(global_prompt)
        print(f"\n[sweeper] Global summary:\n{global_summary}\n")
        write_global_summary(global_summary, project_briefs)
    else:
        print(f"\n[dry-run] Would generate global summary from {len(project_briefs)} briefs")

    print(f"\n[sweeper] Done. {now_utc()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-project intelligence sweep")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--list", action="store_true", help="List registered projects")
    parser.add_argument("--register", metavar="PATH", help="Register a new project")
    args = parser.parse_args()

    if args.list:
        cmd_list()
    elif args.register:
        cmd_register(args.register)
    else:
        cmd_sweep(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
