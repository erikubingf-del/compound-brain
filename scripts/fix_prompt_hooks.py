#!/usr/bin/env python3
"""
fix_prompt_hooks.py — Remove prompt-type Stop hooks from all settings files.

Claude Code no longer supports prompt-type hooks at the Stop event.
Any settings.json or settings.local.json with a prompt-type Stop hook will
produce "Stop hook error: JSON validation failed" on every session end.

This script:
  1. Fixes ~/.claude/settings.json (global)
  2. Fixes every .claude/settings.local.json in all registered activated repos
  3. Reports what was changed

Safe to run multiple times — only touches files that still have the issue.
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path


def _claude_home() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_HOME")
    return Path(override) if override else Path.home() / ".claude"


def _backup(path: Path) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = path.with_suffix(f".bak-{ts}.json")
    shutil.copy2(path, backup)
    return backup


_UNSUPPRESSED_STOP = "python3 .claude/hooks/project_stop.py"
_SUPPRESSED_STOP   = "python3 .claude/hooks/project_stop.py > /dev/null 2>&1"


def _has_prompt_stop_hook(settings: dict) -> bool:
    for group in settings.get("hooks", {}).get("Stop", []):
        for hook in group.get("hooks", []):
            if hook.get("type") == "prompt":
                return True
    return False


def _has_unsuppressed_stop(settings: dict) -> bool:
    for group in settings.get("hooks", {}).get("Stop", []):
        for hook in group.get("hooks", []):
            if hook.get("command", "").strip() == _UNSUPPRESSED_STOP:
                return True
    return False


def _remove_prompt_stop_hooks(settings: dict) -> tuple[dict, int]:
    """Remove prompt-type Stop hooks and fix unsuppressed project_stop.py commands."""
    removed = 0
    stop_groups = settings.get("hooks", {}).get("Stop", [])
    new_stop_groups = []
    for group in stop_groups:
        new_hooks = []
        for h in group.get("hooks", []):
            if h.get("type") == "prompt":
                removed += 1
                continue
            # Fix unsuppressed project_stop.py output
            if h.get("command", "").strip() == _UNSUPPRESSED_STOP:
                h = {**h, "command": _SUPPRESSED_STOP}
            new_hooks.append(h)
        if new_hooks:
            new_stop_groups.append({**group, "hooks": new_hooks})
    if "hooks" in settings and "Stop" in settings["hooks"]:
        if new_stop_groups:
            settings["hooks"]["Stop"] = new_stop_groups
        else:
            del settings["hooks"]["Stop"]
    return settings, removed


def fix_settings_file(path: Path, label: str) -> bool:
    """Fix one settings file. Returns True if a change was made."""
    if not path.exists():
        return False
    try:
        raw = path.read_text(encoding="utf-8")
        settings = json.loads(raw)
    except Exception as e:
        print(f"  ! could not parse {label}: {e}")
        return False

    if not _has_prompt_stop_hook(settings) and not _has_unsuppressed_stop(settings):
        return False

    backup = _backup(path)
    settings, removed = _remove_prompt_stop_hooks(settings)
    path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    print(f"  fixed  {label}  ({removed} prompt hook{'s' if removed != 1 else ''} removed)")
    print(f"         backup → {backup.name}")
    return True


def find_all_settings(claude_home: Path) -> list[Path]:
    """Find every settings*.json under ~/.claude/ and common project roots."""
    seen: set[Path] = set()
    paths: list[Path] = []

    def add(p: Path) -> None:
        rp = p.resolve()
        if rp not in seen and rp.exists():
            seen.add(rp)
            paths.append(p)

    home = Path.home()

    # Global template
    add(claude_home / "templates" / "project_claude" / "settings.local.json")

    # Registered activated repos
    registry_path = claude_home / "registry" / "activated-projects.json"
    if registry_path.exists():
        try:
            registry = json.loads(registry_path.read_text())
            entries = registry if isinstance(registry, list) else registry.get("projects", [])
            for entry in entries:
                repo_dir = Path(str(entry.get("path", "") or (entry if isinstance(entry, str) else "")))
                add(repo_dir / ".claude" / "settings.local.json")
                add(repo_dir / ".claude" / "settings.json")
        except Exception:
            pass

    # Broad filesystem scan — covers GitHub, crm, worktrees, etc.
    scan_roots = [
        home / "Documents" / "GitHub",
        home / "crm",
        home / ".claude-worktrees",
    ]
    for root in scan_roots:
        if root.is_dir():
            for p in root.rglob(".claude/settings*.json"):
                if ".git" not in p.parts and "node_modules" not in p.parts:
                    add(p)

    return paths


def main() -> None:
    claude_home = _claude_home()
    print("compound-brain: scanning for prompt-type Stop hooks...\n")

    changed = 0

    # 1. Global settings
    global_settings = claude_home / "settings.json"
    if fix_settings_file(global_settings, "~/.claude/settings.json"):
        changed += 1

    # 2. All settings files system-wide
    project_settings = find_all_settings(claude_home)
    for path in project_settings:
        repo_name = path.parents[1].name
        if fix_settings_file(path, f"{repo_name}/.claude/settings.local.json"):
            changed += 1

    if changed:
        print(f"\n✓ Fixed {changed} file{'s' if changed != 1 else ''}.")
        print("  The 'Stop hook error: JSON validation failed' error will not recur.")
    else:
        print("✓ No prompt-type Stop hooks found — nothing to fix.")


if __name__ == "__main__":
    main()
