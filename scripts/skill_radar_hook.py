#!/usr/bin/env python3
"""
skill_radar_hook.py — SessionStart hook for compound-brain skill radar.

Responsibilities:
  1. Check whether the global skill-catalog.json is stale.
     If stale, trigger skill_radar_refresh.py asynchronously (non-blocking)
     so the next session gets fresh data without delaying this one.
  2. Read .brain/state/skills.json for the current repo.
     Surface any new recommended skills (from the latest radar run) as a
     visible message so Claude can act on them, not just find them in a file.
  3. Surface any high-confidence project tips from the tip catalog that
     are relevant to this repo's departments.

Silent if:
  - not in an activated repo (no .brain/state/skills.json)
  - no new recommended skills and no relevant tips
  - skill state file is malformed
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


STALE_HOURS = 12          # refresh if catalog older than this
TIP_MIN_CONFIDENCE = 0.7  # only surface high-confidence tips
MAX_TIPS_SHOWN = 3        # cap to avoid noise
MAX_SKILLS_SHOWN = 5


def _claude_home() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_HOME")
    return Path(override) if override else Path.home() / ".claude"


def _catalog_age_hours(catalog_path: Path) -> float | None:
    """Return age in hours of the skill catalog, or None if missing."""
    if not catalog_path.exists():
        return None
    try:
        data = json.loads(catalog_path.read_text())
        generated_at = data.get("generated_at")
        if not generated_at:
            return None
        ts = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
        return age
    except Exception:
        return None


def _trigger_async_refresh(claude_home: Path, project_dir: Path) -> None:
    """Fire skill_radar_refresh.py in the background — does not block."""
    script = claude_home / "scripts" / "skill_radar_refresh.py"
    if not script.exists():
        return
    try:
        subprocess.Popen(
            [sys.executable, str(script), "--project-dir", str(project_dir)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def _load_skills(project_dir: Path) -> dict | None:
    skills_path = project_dir / ".brain" / "state" / "skills.json"
    if not skills_path.exists():
        return None
    try:
        return json.loads(skills_path.read_text())
    except Exception:
        return None


def _load_tips(claude_home: Path, repo_name: str, departments: list[str]) -> list[dict]:
    tip_path = claude_home / "knowledge" / "resources" / "project-tip-catalog.json"
    if not tip_path.exists():
        return []
    try:
        data = json.loads(tip_path.read_text())
        tips = []
        for tip in data.get("tips", []):
            conf = float(tip.get("confidence", 0))
            dept = str(tip.get("department", ""))
            src = str(tip.get("source_repo", ""))
            if src == repo_name:
                continue  # skip self-generated tips
            if conf < TIP_MIN_CONFIDENCE:
                continue
            if departments and dept and dept not in departments:
                continue
            tips.append(tip)
        # sort by confidence desc, take top N
        tips.sort(key=lambda t: float(t.get("confidence", 0)), reverse=True)
        return tips[:MAX_TIPS_SHOWN]
    except Exception:
        return []


def main() -> None:
    cwd = Path(os.getcwd())
    claude_home = _claude_home()
    catalog_path = claude_home / "knowledge" / "resources" / "skill-catalog.json"

    # ── 1. Stale check — trigger async refresh if needed ──────────────────────
    age = _catalog_age_hours(catalog_path)
    stale = age is None or age > STALE_HOURS
    if stale:
        _trigger_async_refresh(claude_home, cwd)

    # ── 2. Load repo skill state ───────────────────────────────────────────────
    skills = _load_skills(cwd)
    if skills is None:
        sys.exit(0)  # not an activated repo

    recommended: list[dict] = skills.get("recommended", [])
    active: list[str] = [
        s.get("name", s) if isinstance(s, dict) else s
        for s in skills.get("active", [])
    ]

    # Filter to truly new recommendations (not already active)
    new_skills = [
        s for s in recommended
        if (s.get("name") if isinstance(s, dict) else s) not in active
    ][:MAX_SKILLS_SHOWN]

    # ── 3. Load relevant project tips ─────────────────────────────────────────
    repo_name = cwd.name
    departments: list[str] = skills.get("departments", [])
    tips = _load_tips(claude_home, repo_name, departments)

    # ── 4. Surface to Claude ───────────────────────────────────────────────────
    has_output = new_skills or tips or stale
    if not has_output:
        sys.exit(0)

    lines: list[str] = []
    sep = "─" * 55

    lines.append(f"\n{sep}")
    lines.append("  Skill Radar")
    if stale:
        age_label = "no cache" if age is None else f"{age:.0f}h old"
        lines.append(f"  catalog: {age_label} — async refresh triggered")
    else:
        lines.append(f"  catalog: {age:.0f}h old")
    lines.append(sep)

    if new_skills:
        lines.append("  New skill recommendations for this repo:")
        for skill in new_skills:
            if isinstance(skill, dict):
                name = skill.get("name", "?")
                reason = skill.get("match_reason") or skill.get("reason") or ""
                dept = skill.get("department", "")
                tag = f"[{dept}] " if dept else ""
                reason_str = f" — {reason}" if reason else ""
                lines.append(f"    + {tag}{name}{reason_str}")
            else:
                lines.append(f"    + {skill}")
        lines.append("  → Review .brain/state/skills.json to approve")

    if tips:
        if new_skills:
            lines.append("")
        lines.append("  Project tips from other activated repos:")
        for tip in tips:
            dept = tip.get("department", "")
            tip_text = tip.get("tip", "")
            conf = float(tip.get("confidence", 0))
            dept_label = f"[{dept}] " if dept else ""
            lines.append(f"    · {dept_label}{tip_text}  (conf: {conf:.2f})")

    lines.append(sep)
    lines.append("")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
