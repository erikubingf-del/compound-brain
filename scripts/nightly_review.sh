#!/usr/bin/env bash
# compound-brain nightly review and stop-hook wrapper

set -euo pipefail

PYTHON_BIN="__PYTHON_BIN__"
CLAUDE_HOME="${COMPOUND_BRAIN_HOME:-${HOME}/.claude}"

if [[ -d ".brain" ]]; then
  "${PYTHON_BIN}" "${CLAUDE_HOME}/scripts/project_intelligence.py" --project-dir "$PWD" >/dev/null 2>&1 || true
fi

"${PYTHON_BIN}" "${CLAUDE_HOME}/scripts/review_promotion_inbox.py" >/dev/null 2>&1 || true
"${PYTHON_BIN}" "${CLAUDE_HOME}/scripts/apply_approved_promotions.py" >/dev/null 2>&1 || true

if [[ -f ".brain/architecture/evaluator.md" && -f "${CLAUDE_HOME}/scripts/update_architecture_scorecard.py" ]]; then
  "${PYTHON_BIN}" "${CLAUDE_HOME}/scripts/update_architecture_scorecard.py" --repo-root "$PWD" >/dev/null 2>&1 || true
fi
