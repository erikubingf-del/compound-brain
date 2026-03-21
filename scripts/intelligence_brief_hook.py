#!/usr/bin/env python3
"""
intelligence_brief_hook.py — SessionStart hook reader for AI intelligence briefs.

Reads the latest intelligence brief from the current project's .brain/ directory
and surfaces it at session start. Silent if no brief exists.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

cwd = Path(os.getcwd())
brief_path = cwd / ".brain" / "knowledge" / "daily" / "intelligence_brief_latest.md"

if not brief_path.exists():
    sys.exit(0)

# Check if brief is stale (older than 8 hours — don't surface outdated intel)
mtime = brief_path.stat().st_mtime
age_hours = (datetime.now(timezone.utc).timestamp() - mtime) / 3600
if age_hours > 8:
    sys.exit(0)

content = brief_path.read_text(encoding="utf-8").strip()
if not content:
    sys.exit(0)

age_label = f"{age_hours:.0f}h ago" if age_hours >= 1 else f"{age_hours * 60:.0f}m ago"

print(f"\n{'─' * 55}")
print(f"  AI Intelligence Brief  ({age_label})")
print(f"{'─' * 55}")
print(content)
print(f"{'─' * 55}\n")
