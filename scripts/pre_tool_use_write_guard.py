#!/usr/bin/env python3
"""
PreToolUse — Dept Write Guard.

Fires before Edit/Write tool calls. Reads dept contracts from
.claude/departments/*.md in the project root, extracts "Protected Surfaces"
path patterns, and blocks writes to those paths.

Completely silent if:
- No dept contracts found
- No protected path patterns match
- Not in a real project

Input (stdin): JSON with tool_name, tool_input
Output (stdout): block message (exit 2 blocks the tool call)
Exit 0 = allow, Exit 2 = block
"""

from __future__ import annotations
import fnmatch
import json
import re
import sys
from pathlib import Path

# ── Read hook payload ──────────────────────────────────────────────────────────
try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_name = payload.get("tool_name", "")
if tool_name not in ("Edit", "Write"):
    sys.exit(0)

tool_input = payload.get("tool_input", {})
file_path = tool_input.get("file_path", "")
if not file_path:
    sys.exit(0)

# ── Detect project root ────────────────────────────────────────────────────────
target = Path(file_path)
cwd = Path.cwd()

project_root: Path | None = None
check = target.parent if target.is_absolute() else cwd
for parent in [check] + list(check.parents):
    if (parent / ".git").exists():
        project_root = parent
        break

if not project_root:
    sys.exit(0)

try:
    rel_path = str(target.relative_to(project_root)) if target.is_absolute() else str(target)
except ValueError:
    rel_path = str(target)

# ── Find dept contracts ────────────────────────────────────────────────────────
dept_dir = project_root / ".claude" / "departments"
if not dept_dir.exists():
    sys.exit(0)

dept_files = sorted(dept_dir.glob("*.md"))
if not dept_files:
    sys.exit(0)

# ── Extract path-like tokens from Protected Surfaces ─────────────────────────
PATH_LIKE = re.compile(
    r'`([^`]+)`'           # backtick-quoted token
    r'|(\S+/\S*)'          # anything with a slash (path-like)
    r'|(\.\w[\w.-]*)'      # dotfile pattern e.g. .env.local
)

def extract_protected_patterns(contract_text: str) -> list[str]:
    """Pull path-like entries from the ## Protected Surfaces section."""
    match = re.search(
        r'## Protected Surfaces\s*\n(.*?)(?=\n## |\Z)', contract_text, re.DOTALL
    )
    if not match:
        return []
    section = match.group(1)
    patterns: list[str] = []
    for line in section.splitlines():
        stripped = line.strip().lstrip("- ").strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Extract all path-like tokens from this line
        for m in PATH_LIKE.finditer(stripped):
            token = m.group(1) or m.group(2) or m.group(3)
            if token:
                token = token.strip("`").strip()
                # Only keep tokens that look like real paths (contain / or start with .)
                if "/" in token or token.startswith("."):
                    patterns.append(token)
    return patterns

def matches_pattern(rel: str, pattern: str) -> bool:
    """Match rel path against a protected pattern."""
    # Exact match
    if fnmatch.fnmatch(rel, pattern):
        return True
    # Basename match
    if fnmatch.fnmatch(Path(rel).name, Path(pattern).name):
        # Only match if the line explicitly named this file (no wildcards in pattern)
        if "*" not in pattern and "/" not in pattern:
            return True
    # Prefix/directory match: src/lib/storage/ matches src/lib/storage/foo.ts
    clean = pattern.rstrip("/")
    if rel.startswith(clean + "/") or rel == clean:
        return True
    # Glob match with **
    if "**" in pattern and fnmatch.fnmatch(rel, pattern):
        return True
    return False

# ── Check each contract ────────────────────────────────────────────────────────
blocking_dept: str | None = None
blocking_pattern: str | None = None

for dept_file in dept_files:
    try:
        text = dept_file.read_text(errors="ignore")
    except Exception:
        continue

    patterns = extract_protected_patterns(text)
    for pat in patterns:
        if matches_pattern(rel_path, pat):
            blocking_dept = dept_file.stem
            blocking_pattern = pat
            break
    if blocking_dept:
        break

if not blocking_dept:
    sys.exit(0)

# ── Emit block message ─────────────────────────────────────────────────────────
print(f"BLOCKED — {rel_path} is a protected surface.")
print(f"Owning dept: {blocking_dept}  |  Pattern: {blocking_pattern}")
print()
print("This path is listed under 'Protected Surfaces' in the dept contract.")
print("To proceed: confirm the change is in scope and required, then edit the")
print(f".claude/departments/{blocking_dept}.md contract to explicitly permit this write,")
print("or log an approval entry in .brain/state/pending-approvals.md.")
sys.exit(2)
