#!/usr/bin/env bash
# compound-brain installer
# Sets up the global brain, hooks, and cron jobs.
# Usage: bash install.sh [--dry-run] [--unattended]

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRAIN_DIR="${HOME}/.claude"
KNOWLEDGE_DIR="${BRAIN_DIR}/knowledge"
SCRIPTS_DIR="${BRAIN_DIR}/scripts"
LIB_DIR="${SCRIPTS_DIR}/lib"
REGISTRY_DIR="${BRAIN_DIR}/registry"
TEMPLATES_DIR="${BRAIN_DIR}/templates/project_claude"
CODEX_TEMPLATES_DIR="${BRAIN_DIR}/templates/project_codex"
SETTINGS_FILE="${BRAIN_DIR}/settings.json"
CONFIG_FILE="${BRAIN_DIR}/intelligence_projects.json"
DRY_RUN=false
UNATTENDED=false

# ─── Colors ─────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; RESET='\033[0m'
ok()   { echo -e "${GREEN}  ✓${RESET} $1"; }
warn() { echo -e "${YELLOW}  ⚠${RESET} $1"; }
err()  { echo -e "${RED}  ✗${RESET} $1"; }
run()  { $DRY_RUN && echo "  [dry-run] $*" || eval "$@"; }

for arg in "$@"; do
  case $arg in
    --dry-run)    DRY_RUN=true ;;
    --unattended) UNATTENDED=true ;;
  esac
done

# ─── Detect Claude binary ────────────────────────────────────────────────────
detect_claude() {
  for candidate in \
    "${HOME}/.local/bin/claude" \
    "/usr/local/bin/claude" \
    "/opt/homebrew/bin/claude" \
    "$(which claude 2>/dev/null || true)"
  do
    if [[ -x "$candidate" ]]; then
      echo "$candidate"
      return 0
    fi
  done
  echo ""
}

CLAUDE_BIN=$(detect_claude)
if [[ -z "$CLAUDE_BIN" ]]; then
  warn "claude binary not found — intelligence scripts will fail until Claude Code is installed"
  warn "Install Claude Code: https://claude.ai/download"
  CLAUDE_BIN="claude"
else
  ok "Found claude binary: $CLAUDE_BIN"
fi

# ─── Detect Python ───────────────────────────────────────────────────────────
PYTHON_BIN=""
for candidate in python3 python; do
  if command -v "$candidate" &>/dev/null; then
    PYTHON_BIN=$(command -v "$candidate")
    break
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  err "Python 3 not found — required for intelligence scripts"
  exit 1
fi
ok "Found python: $PYTHON_BIN"

echo ""
echo "────────────────────────────────────────────"
echo "  compound-brain installer"
echo "  Installing to: $BRAIN_DIR"
echo "  Lifecycle: observe -> preview -> prepare -> activate"
echo "────────────────────────────────────────────"
echo ""

# ─── Step 1: Create directory structure ─────────────────────────────────────
echo "[ 1/7 ] Creating global brain directories..."
for dir in \
  "$KNOWLEDGE_DIR/daily" \
  "$KNOWLEDGE_DIR/weekly" \
  "$KNOWLEDGE_DIR/projects" \
  "$KNOWLEDGE_DIR/areas" \
  "$KNOWLEDGE_DIR/resources" \
  "$KNOWLEDGE_DIR/archives" \
  "$KNOWLEDGE_DIR/decisions" \
  "$KNOWLEDGE_DIR/skills" \
  "$KNOWLEDGE_DIR/qmp" \
  "$KNOWLEDGE_DIR/promotions" \
  "$REGISTRY_DIR" \
  "$SCRIPTS_DIR" \
  "$LIB_DIR" \
  "$TEMPLATES_DIR/hooks" \
  "$TEMPLATES_DIR/departments" \
  "$TEMPLATES_DIR/autoresearch" \
  "$CODEX_TEMPLATES_DIR" \
  "${BRAIN_DIR}/hooks"
do
  run "mkdir -p \"$dir\""
done
ok "Directories created"

# ─── Step 2: Install scripts ─────────────────────────────────────────────────
echo ""
echo "[ 2/7 ] Installing scripts..."
SCRIPTS=(
  "activate_repo.py"
  "architecture_radar.py"
  "materialize_project_claude.py"
  "prepare_brain.py"
  "project_intelligence.py"
  "global_intelligence_sweeper.py"
  "intelligence_brief_hook.py"
  "project_auditor.py"
  "probability_engine.py"
  "run_project_llm_cron.py"
  "github_intelligence.py"
  "setup_brain.sh"
  "nightly_review.sh"
)
for script in "${SCRIPTS[@]}"; do
  src="${REPO_DIR}/scripts/${script}"
  dst="${SCRIPTS_DIR}/${script}"
  if [[ -f "$src" ]]; then
    # Inject correct CLAUDE_BIN and PYTHON_BIN
    run "sed 's|__CLAUDE_BIN__|${CLAUDE_BIN}|g; s|__PYTHON_BIN__|${PYTHON_BIN}|g' \"$src\" > \"$dst\""
    run "chmod +x \"$dst\""
    ok "Installed: $script"
  else
    warn "Not found (skipping): $script"
  fi
done

for lib_file in "${REPO_DIR}/scripts/lib/"*.py; do
  [[ -f "$lib_file" ]] || continue
  fname=$(basename "$lib_file")
  run "cp \"$lib_file\" \"${LIB_DIR}/${fname}\""
  ok "Installed library: $fname"
done

for template_file in "${REPO_DIR}/templates/project_claude/"*.md \
                      "${REPO_DIR}/templates/project_claude/"*.json \
                      "${REPO_DIR}/templates/project_claude/hooks/"*.py \
                      "${REPO_DIR}/templates/project_claude/departments/"*.md \
                      "${REPO_DIR}/templates/project_claude/autoresearch/"*.md; do
  [[ -f "$template_file" ]] || continue
  rel_path="${template_file#${REPO_DIR}/templates/project_claude/}"
  run "mkdir -p \"$(dirname "${TEMPLATES_DIR}/${rel_path}")\""
  run "cp \"$template_file\" \"${TEMPLATES_DIR}/${rel_path}\""
  ok "Installed template: $rel_path"
done

for template_file in "${REPO_DIR}/templates/project_codex/"*.md; do
  [[ -f "$template_file" ]] || continue
  rel_path="${template_file#${REPO_DIR}/templates/project_codex/}"
  run "mkdir -p \"$(dirname "${CODEX_TEMPLATES_DIR}/${rel_path}")\""
  run "cp \"$template_file\" \"${CODEX_TEMPLATES_DIR}/${rel_path}\""
  ok "Installed Codex template: $rel_path"
done

# ─── Step 3: Seed knowledge base ─────────────────────────────────────────────
echo ""
echo "[ 3/7 ] Seeding knowledge base..."

# BRAIN.md (master instructions)
if [[ ! -f "${BRAIN_DIR}/BRAIN.md" ]]; then
  run "cp \"${REPO_DIR}/core/BRAIN.md\" \"${BRAIN_DIR}/BRAIN.md\""
  ok "Installed: BRAIN.md"
else
  warn "BRAIN.md already exists — skipping (to reset: cp ${REPO_DIR}/core/BRAIN.md ${BRAIN_DIR}/BRAIN.md)"
fi

# QMP entries
for qmp_file in "${REPO_DIR}/knowledge-seed/qmp/"*.md; do
  fname=$(basename "$qmp_file")
  dst="${KNOWLEDGE_DIR}/qmp/${fname}"
  if [[ ! -f "$dst" ]]; then
    run "cp \"$qmp_file\" \"$dst\""
    ok "Seeded QMP: $fname"
  fi
done

# QMP index
if [[ ! -f "${KNOWLEDGE_DIR}/qmp/_index.md" ]]; then
  run "cp \"${REPO_DIR}/knowledge-seed/qmp/_index.md\" \"${KNOWLEDGE_DIR}/qmp/_index.md\""
fi

# Resources
for res_file in "${REPO_DIR}/knowledge-seed/resources/"*.md; do
  fname=$(basename "$res_file")
  dst="${KNOWLEDGE_DIR}/resources/${fname}"
  if [[ ! -f "$dst" ]]; then
    run "cp \"$res_file\" \"$dst\""
    ok "Seeded resource: $fname"
  fi
done

# Skill graph seed
if [[ ! -f "${KNOWLEDGE_DIR}/skills/skill-graph.md" ]]; then
  run "cp \"${REPO_DIR}/knowledge-seed/skills/skill-graph.md\" \"${KNOWLEDGE_DIR}/skills/skill-graph.md\""
  ok "Seeded: skill-graph.md"
fi

# Decision log seed
if [[ ! -f "${KNOWLEDGE_DIR}/decisions/log.md" ]]; then
  cat > "${KNOWLEDGE_DIR}/decisions/log.md" <<'EOF'
# Decision Log

> Every strategic decision that affects architecture, product direction, deployment,
> data safety, cost structure, or workflow standards must be logged here.

## Template

```markdown
## DEC-XXX — Decision title
**Date:** YYYY-MM-DD
**Priority:** P1 | P2 | P3
**Context:** Why this decision was needed
**Options Considered:** What else was considered
**Reasoning:** Why this option was chosen
**Expected Outcome:** What should happen
**Actual Outcome:** Filled in later
**Rule established:** If this creates a lasting rule
```

---

EOF
  ok "Created: decisions/log.md"
fi

# knowledge index
if [[ ! -f "${KNOWLEDGE_DIR}/_index.md" ]]; then
  cat > "${KNOWLEDGE_DIR}/_index.md" <<'EOF'
# Knowledge Index

## Projects
<!-- Active projects with defined outcomes -->

## Areas
<!-- Ongoing responsibilities with no fixed end date -->

## Resources
<!-- Reusable reference knowledge and patterns -->

## QMP Library
See [qmp/_index.md](qmp/_index.md) for the full Question-Model-Process library.

## Skills
See [skills/skill-graph.md](skills/skill-graph.md) for the skill capability map.

## Decision Log
See [decisions/log.md](decisions/log.md) for the strategic decision history.
EOF
  ok "Created: _index.md"
fi

# ─── Step 4: Configure Claude Code hooks ────────────────────────────────────
echo ""
echo "[ 4/7 ] Configuring Claude Code hooks..."

HOOK_SCRIPT="${SCRIPTS_DIR}/intelligence_brief_hook.py"
HEALTH_SCRIPT="${SCRIPTS_DIR}/universal_project_health.py"
SESSION_END_SCRIPT="${SCRIPTS_DIR}/nightly_review.sh"
PROJECT_CRON_SCRIPT="${SCRIPTS_DIR}/run_project_llm_cron.py"

if [[ ! -f "$SETTINGS_FILE" ]]; then
  # Create fresh settings.json
  if $DRY_RUN; then
    echo "  [dry-run] write ${SETTINGS_FILE} with shared session hooks"
  else
    cat > "$SETTINGS_FILE" <<EOF
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${SCRIPTS_DIR}/setup_brain.sh\" --check-only 2>/dev/null"
          },
          {
            "type": "command",
            "command": "${PYTHON_BIN} \"${SCRIPTS_DIR}/intelligence_brief_hook.py\" 2>/dev/null",
            "timeout": 3,
            "statusMessage": "Loading AI intelligence brief..."
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${PYTHON_BIN} \"${SCRIPTS_DIR}/nightly_review.sh\" 2>/dev/null",
            "timeout": 8
          }
        ]
      }
    ]
  }
}
EOF
    ok "Created: settings.json with hooks"
  fi
else
  warn "settings.json already exists — add these hooks manually or check docs/HOOKS_GUIDE.md"
  warn "Hook to add to SessionStart:"
  echo "    {\"type\":\"command\",\"command\":\"${PYTHON_BIN} ${HOOK_SCRIPT} 2>/dev/null\",\"timeout\":3}"
fi

# ─── Step 5: Project registry ────────────────────────────────────────────────
echo ""
echo "[ 5/7 ] Setting up project registry..."

if [[ ! -f "$CONFIG_FILE" ]]; then
  if $DRY_RUN; then
    echo "  [dry-run] write ${CONFIG_FILE}"
  else
    cat > "$CONFIG_FILE" <<EOF
{
  "auto_discover": true,
  "max_projects_per_run": 5,
  "projects": []
}
EOF
    ok "Created: intelligence_projects.json (empty — add projects with: python3 ${SCRIPTS_DIR}/global_intelligence_sweeper.py --register /path/to/project)"
  fi
else
  warn "intelligence_projects.json already exists — skipping"
fi

# ─── Step 6: Crontab ─────────────────────────────────────────────────────────
echo ""
echo "[ 6/7 ] Setting up cron jobs..."

install_cron() {
  local marker="$1"
  local entry="$2"
  if $DRY_RUN; then
    echo "  [dry-run] cron ${marker}: ${entry}"
    return 0
  fi
  if crontab -l 2>/dev/null | grep -q "$marker"; then
    warn "Cron already exists: $marker"
  else
    (crontab -l 2>/dev/null; echo "$entry") | crontab -
    ok "Cron added: $marker"
  fi
}

install_cron "COMPOUND_GLOBAL_SWEEP" \
  "30 */6 * * * ${PYTHON_BIN} ${SCRIPTS_DIR}/global_intelligence_sweeper.py >> /tmp/compound_global_sweep.log 2>&1 # COMPOUND_GLOBAL_SWEEP"

install_cron "COMPOUND_PROJECT_LLM_CRON" \
  "0 */6 * * * ${PYTHON_BIN} ${PROJECT_CRON_SCRIPT} >> /tmp/compound_project_llm_cron.log 2>&1 # COMPOUND_PROJECT_LLM_CRON"

install_cron "COMPOUND_GITHUB_INTEL" \
  "0 9 * * 0 ${PYTHON_BIN} ${SCRIPTS_DIR}/github_intelligence.py >> /tmp/compound_github_intel.log 2>&1 # COMPOUND_GITHUB_INTEL"

install_cron "COMPOUND_ARCH_GUARDIAN" \
  "0 10 * * 0 ${PYTHON_BIN} ${SCRIPTS_DIR}/project_auditor.py --all-registered >> /tmp/compound_audit.log 2>&1 # COMPOUND_ARCH_GUARDIAN"

# ─── Step 7: Gitignore for brain ─────────────────────────────────────────────
echo ""
echo "[ 7/7 ] Finalizing..."

# Create global gitignore pattern for .brain (optional - project-specific)
if $DRY_RUN; then
  echo "  [dry-run] write ${REPO_DIR}/.brain-gitignore-template"
else
  cat > "${REPO_DIR}/.brain-gitignore-template" <<'EOF'
# Add to your project's .gitignore to keep brain files local:
# .brain/memory/*.md     — sensitive session state
# .brain/knowledge/daily/ — raw operational logs
#
# Keep these tracked (shared team intelligence):
# .brain/knowledge/projects/
# .brain/knowledge/decisions/
# .brain/knowledge/resources/
# .brain/knowledge/qmp/
# .brain/knowledge/skills/
EOF
  ok "Created: .brain-gitignore-template"
fi

# ─── Done ────────────────────────────────────────────────────────────────────
echo ""
echo "────────────────────────────────────────────"
echo -e "${GREEN}  compound-brain installed!${RESET}"
echo "────────────────────────────────────────────"
echo ""
echo "  Next steps:"
echo ""
echo "  1. Preview a repo without writing repo files:"
echo "     ${PYTHON_BIN} ${SCRIPTS_DIR}/activate_repo.py --project-dir /path/to/your/project --check-only"
echo ""
echo "  2. Prepare static project memory:"
echo "     ${PYTHON_BIN} ${SCRIPTS_DIR}/prepare_brain.py /path/to/your/project"
echo ""
echo "  3. Activate full repo autonomy:"
echo "     ${PYTHON_BIN} ${SCRIPTS_DIR}/activate_repo.py --project-dir /path/to/your/project"
echo ""
echo "  4. Open Claude Code in your project after activation:"
echo "     cd /path/to/your/project && claude"
echo ""
echo "  Shared cron runs every 6h. Next run: $(date -d '+6 hours' '+%H:%M' 2>/dev/null || date -v+6H '+%H:%M')"
echo ""
