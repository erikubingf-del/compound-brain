#!/usr/bin/env python3
"""Repo-local session-start hook for [PROJECT_NAME]."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


repo_dir = Path(__file__).resolve().parents[2]
claude_home = Path(os.environ.get("COMPOUND_BRAIN_HOME", str(Path.home() / ".claude")))
script = claude_home / "scripts" / "project_runtime_event.py"
raise SystemExit(
    subprocess.call(
        ["python3", str(script), "--event", "session-start", "--project-dir", str(repo_dir)]
    )
)
