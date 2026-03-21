#!/usr/bin/env bash
# setup_brain.sh — Scaffold or check a .brain/ directory for a project
#
# Usage:
#   bash setup_brain.sh /path/to/project [project-name] [description]
#   bash setup_brain.sh --check-only        # scaffold if missing in $PWD
#   bash setup_brain.sh --list              # list all known project brains
#
# Installed by compound-brain to: ~/.claude/scripts/setup_brain.sh

set -euo pipefail

BRAIN_TEMPLATE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/brain-template"
# Fallback: if running from installed location, template is not adjacent
if [[ ! -d "$BRAIN_TEMPLATE_DIR" ]]; then
  # Installed scripts live in ~/.claude/scripts — template not packaged there.
  # We'll construct the scaffold inline instead.
  BRAIN_TEMPLATE_DIR=""
fi

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RESET='\033[0m'
ok()   { echo -e "${GREEN}  ✓${RESET} $1"; }
note() { echo -e "${YELLOW}  →${RESET} $1"; }

# ─── Argument parsing ────────────────────────────────────────────────────────
CHECK_ONLY=false
LIST_MODE=false
PROJECT_DIR=""
PROJECT_NAME=""
PROJECT_DESC=""

for arg in "$@"; do
  case $arg in
    --check-only) CHECK_ONLY=true ;;
    --list)       LIST_MODE=true ;;
    *)
      if [[ -z "$PROJECT_DIR" ]]; then
        PROJECT_DIR="$arg"
      elif [[ -z "$PROJECT_NAME" ]]; then
        PROJECT_NAME="$arg"
      elif [[ -z "$PROJECT_DESC" ]]; then
        PROJECT_DESC="$arg"
      fi
      ;;
  esac
done

# ─── List mode ───────────────────────────────────────────────────────────────
if $LIST_MODE; then
  echo "Known project brains:"
  if [[ -f "${HOME}/.claude/intelligence_projects.json" ]]; then
    python3 -c "
import json, os
data = json.load(open(os.path.expanduser('~/.claude/intelligence_projects.json')))
for p in data.get('projects', []):
    brain = os.path.join(p, '.brain')
    status = '✓' if os.path.isdir(brain) else '✗ (brain missing)'
    print(f'  {status}  {p}')
" 2>/dev/null || echo "  (none registered)"
  else
    echo "  (no registry found)"
  fi
  exit 0
fi

# ─── Check-only mode: scaffold PWD if .brain is missing ──────────────────────
if $CHECK_ONLY; then
  PROJECT_DIR="$PWD"
  PROJECT_NAME="$(basename "$PWD")"
  PROJECT_DESC=""
  # Only scaffold if it's a real project directory
  if [[ ! -f "$PROJECT_DIR/.git/config" ]] && \
     [[ ! -f "$PROJECT_DIR/package.json" ]] && \
     [[ ! -f "$PROJECT_DIR/pyproject.toml" ]] && \
     [[ ! -f "$PROJECT_DIR/Cargo.toml" ]] && \
     [[ ! -f "$PROJECT_DIR/go.mod" ]] && \
     [[ ! -f "$PROJECT_DIR/Makefile" ]]; then
    exit 0  # Not a real project dir — skip silently
  fi
  if [[ -d "$PROJECT_DIR/.brain" ]]; then
    exit 0  # Already has a brain — nothing to do
  fi
  echo "No .brain/ found — scaffolding project brain for: $PROJECT_NAME"
fi

# ─── Resolve project dir ─────────────────────────────────────────────────────
if [[ -z "$PROJECT_DIR" ]]; then
  echo "Usage: bash setup_brain.sh /path/to/project [project-name] [description]"
  echo "       bash setup_brain.sh --check-only"
  echo "       bash setup_brain.sh --list"
  exit 1
fi

PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
if [[ -z "$PROJECT_NAME" ]]; then
  PROJECT_NAME="$(basename "$PROJECT_DIR")"
fi
TODAY="$(date +%Y-%m-%d)"

BRAIN_DIR="${PROJECT_DIR}/.brain"
KNOWLEDGE_DIR="${BRAIN_DIR}/knowledge"
MEMORY_DIR="${BRAIN_DIR}/memory"
STATE_DIR="${BRAIN_DIR}/state"

echo ""
echo "  Scaffolding .brain/ for: $PROJECT_NAME"
echo "  Location: $BRAIN_DIR"
echo ""

# ─── Create directory structure ──────────────────────────────────────────────
for dir in \
  "${KNOWLEDGE_DIR}/daily" \
  "${KNOWLEDGE_DIR}/weekly" \
  "${KNOWLEDGE_DIR}/projects" \
  "${KNOWLEDGE_DIR}/areas" \
  "${KNOWLEDGE_DIR}/resources" \
  "${KNOWLEDGE_DIR}/archives" \
  "${KNOWLEDGE_DIR}/decisions" \
  "${KNOWLEDGE_DIR}/skills" \
  "${KNOWLEDGE_DIR}/qmp" \
  "${KNOWLEDGE_DIR}/crons" \
  "${MEMORY_DIR}" \
  "${STATE_DIR}"
do
  mkdir -p "$dir"
done

# ─── MEMORY.md ───────────────────────────────────────────────────────────────
if [[ ! -f "${BRAIN_DIR}/MEMORY.md" ]]; then
  if [[ -n "$BRAIN_TEMPLATE_DIR" ]] && [[ -f "${BRAIN_TEMPLATE_DIR}/MEMORY.md" ]]; then
    sed "s/\[PROJECT_NAME\]/${PROJECT_NAME}/g" "${BRAIN_TEMPLATE_DIR}/MEMORY.md" \
      > "${BRAIN_DIR}/MEMORY.md"
  else
    cat > "${BRAIN_DIR}/MEMORY.md" <<EOF
# Memory Index — ${PROJECT_NAME}

> This file is auto-loaded at session start. Keep it short — it is a pointer index.

## Feedback
<!-- Add: [filename.md](memory/filename.md) — brief description -->

## Project Context
- [project_context.md](memory/project_context.md) — project goal, stack, current state

## References
<!-- - [references.md](memory/references.md) — key APIs, servers, links -->
EOF
  fi
  ok "Created: MEMORY.md"
fi

# ─── memory/project_context.md ───────────────────────────────────────────────
if [[ ! -f "${MEMORY_DIR}/project_context.md" ]]; then
  if [[ -n "$BRAIN_TEMPLATE_DIR" ]] && [[ -f "${BRAIN_TEMPLATE_DIR}/memory/project_context.md" ]]; then
    sed "s/\[PROJECT_NAME\]/${PROJECT_NAME}/g" \
      "${BRAIN_TEMPLATE_DIR}/memory/project_context.md" \
      > "${MEMORY_DIR}/project_context.md"
  else
    cat > "${MEMORY_DIR}/project_context.md" <<EOF
---
name: project-context
type: project
description: Project goal, tech stack, current state, and operating rules
---

# ${PROJECT_NAME} — Project Context

## Goal
${PROJECT_DESC:-<!-- One sentence: what does success look like for this project? -->}

## Status
active

## Tech Stack
<!-- Languages, frameworks, key libraries -->

## Current State
<!-- What exists today? What is working? What is broken? -->

## Key Decisions
<!-- Major architectural or product decisions already made -->

## Risks
<!-- What could cause this project to fail or stall? -->

## Next Actions
<!-- What are the next 3 most important things to do? -->

## Links
<!-- Key docs, repos, servers, dashboards -->
EOF
  fi
  ok "Created: memory/project_context.md"
fi

# ─── memory/feedback_rules.md ────────────────────────────────────────────────
if [[ ! -f "${MEMORY_DIR}/feedback_rules.md" ]]; then
  cat > "${MEMORY_DIR}/feedback_rules.md" <<EOF
---
name: ${PROJECT_NAME} feedback rules
description: Project-specific feedback and correction rules
type: feedback
---

_(No project-specific feedback rules yet. Add corrections and confirmations as they occur.)_

**How to apply:** Project-level feedback rules override global ones when working in this repo.
EOF
  ok "Created: memory/feedback_rules.md"
fi

# ─── knowledge/projects/<project>.md ────────────────────────────────────────
if [[ ! -f "${KNOWLEDGE_DIR}/projects/${PROJECT_NAME}.md" ]]; then
  cat > "${KNOWLEDGE_DIR}/projects/${PROJECT_NAME}.md" <<EOF
---
title: ${PROJECT_NAME}
status: active
updated: ${TODAY}
---

# ${PROJECT_NAME}

## Goal
${PROJECT_DESC:-<!-- What outcome should this project achieve? -->}

## Status
active

## Scope
<!-- What is in scope for this repo? -->

## Current State
<!-- Current architecture, product state, and known constraints -->

## Key Concepts
<!-- Core ideas or systems in this project -->

## Key Decisions
<!-- Major decisions that shape execution -->

## Risks
<!-- What could slow down or derail this project? -->

## Next Actions
<!-- Highest-priority next steps -->

## Links
<!-- Key docs, services, or related repos -->
EOF
  ok "Created: knowledge/projects/${PROJECT_NAME}.md"
fi

# ─── knowledge/decisions/log.md ──────────────────────────────────────────────
if [[ ! -f "${KNOWLEDGE_DIR}/decisions/log.md" ]]; then
  cat > "${KNOWLEDGE_DIR}/decisions/log.md" <<'EOF'
# Decision Log

> Every strategic decision that affects architecture, product direction, deployment,
> data safety, cost structure, or workflow standards must be logged here.

---
EOF
  ok "Created: knowledge/decisions/log.md"
fi

# ─── knowledge/skills/skill-graph.md ─────────────────────────────────────────
if [[ ! -f "${KNOWLEDGE_DIR}/skills/skill-graph.md" ]]; then
  cat > "${KNOWLEDGE_DIR}/skills/skill-graph.md" <<EOF
# Skill Graph — ${PROJECT_NAME}

> Tracks capability growth for this project. Update when actual capability changes, not just exposure.

## Template

\`\`\`
## Skill Name
**Level:** Beginner | Intermediate | Advanced | Expert
**Related Projects:** ...
**Key Knowledge:** ...
**Next Improvements:** ...
\`\`\`

---
EOF
  ok "Created: knowledge/skills/skill-graph.md"
fi

# ─── knowledge/_index.md ─────────────────────────────────────────────────────
if [[ ! -f "${KNOWLEDGE_DIR}/_index.md" ]]; then
  cat > "${KNOWLEDGE_DIR}/_index.md" <<EOF
# Knowledge Index — ${PROJECT_NAME}

## Projects
<!-- Active work with defined outcomes -->

## Areas
<!-- Ongoing responsibilities -->

## Resources
<!-- Reusable patterns and reference -->

## QMP
<!-- Reusable question-model-process entries -->

## Skills
See [skills/skill-graph.md](skills/skill-graph.md)

## Decisions
See [decisions/log.md](decisions/log.md)
EOF
  ok "Created: knowledge/_index.md"
fi

# ─── Seed today's daily note ─────────────────────────────────────────────────
DAILY="${KNOWLEDGE_DIR}/daily/${TODAY}.md"
if [[ ! -f "$DAILY" ]]; then
  cat > "$DAILY" <<EOF
# ${TODAY} — ${PROJECT_NAME}

## Session Notes
<!-- Captured automatically on brain scaffold -->
- .brain/ initialized for ${PROJECT_NAME}

## Next Actions
<!-- What to pick up next session -->
EOF
  ok "Created: knowledge/daily/${TODAY}.md"
fi

# ─── Done ────────────────────────────────────────────────────────────────────
echo ""
ok ".brain/ scaffolded at: $BRAIN_DIR"
echo ""
note "Next: fill in .brain/memory/project_context.md with current project state"
note "      then run: python3 ~/.claude/scripts/project_auditor.py --project-dir ${PROJECT_DIR}"
echo ""
