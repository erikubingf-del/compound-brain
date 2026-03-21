# compound-brain — Architecture

> System design reference. Read this to understand how the pieces fit together.

---

## What it is

compound-brain is an autonomous intelligence layer for software projects. It installs into
`~/.claude/` and gives every project a persistent, self-improving knowledge base (`/.brain/`)
that accumulates context across sessions, runs background analysis, and surfaces the
highest-priority actions at the start of every session.

The core idea: every session should make the next session more effective.

---

## System diagram

```
┌────────────────────────────────────────────────────────────────┐
│  Developer Machine                                             │
│                                                                │
│  ┌──────────────┐   SessionStart hook    ┌──────────────────┐ │
│  │  Claude Code  │ ──────────────────────▶│ intelligence_    │ │
│  │  (any project)│                        │ brief_hook.py    │ │
│  └──────┬───────┘                        └────────┬─────────┘ │
│         │                                         │           │
│         │ reads                          reads    │           │
│         ▼                                         ▼           │
│  ┌──────────────┐                    ┌────────────────────┐   │
│  │ .brain/       │                   │ intelligence_       │   │
│  │ memory/       │                   │ brief_latest.md     │   │
│  │ knowledge/    │                   │ (written by cron)   │   │
│  └──────┬───────┘                    └────────────────────┘   │
│         │                                                      │
│  ┌──────▼──────────────────────────────────────────────────┐  │
│  │  Cron jobs (every 6h / weekly)                          │  │
│  │                                                         │  │
│  │  project_intelligence.py  ─── reads .brain/ + git log  │  │
│  │  global_intelligence_sweeper.py ─── cross-project       │  │
│  │  github_intelligence.py ──── GitHub search + radar      │  │
│  │  project_auditor.py ───────── monthly deep audit        │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ~/.claude/knowledge/   ← global PARA knowledge base          │
│  <project>/.brain/      ← per-project knowledge base          │
└────────────────────────────────────────────────────────────────┘
```

---

## Components

### Core (installed to `~/.claude/`)

| File | Role |
|------|------|
| `core/BRAIN.md` | Master LLM operating instructions — installed as `~/.claude/BRAIN.md` |
| `install.sh` | One-command setup: directories, scripts, hooks, cron |
| `scripts/setup_brain.sh` | Scaffold `.brain/` for a new project |

### Scripts (installed to `~/.claude/scripts/`)

| Script | Trigger | Output |
|--------|---------|--------|
| `project_intelligence.py` | Cron every 6h | `.brain/knowledge/daily/intelligence_brief_latest.md` |
| `global_intelligence_sweeper.py` | Cron every 6h | `~/.claude/knowledge/daily/global_sweep_latest.md` |
| `intelligence_brief_hook.py` | SessionStart hook | Surfaces latest brief to Claude |
| `project_auditor.py` | Monthly cron + on-demand | `.brain/knowledge/areas/project-audit.md` |
| `probability_engine.py` | On-demand | Ranked list of highest-EV actions |
| `github_intelligence.py` | Weekly cron | `.brain/knowledge/resources/github-intel.md` + `architecture-radar.md` |
| `nightly_review.sh` | Stop hook | Appends session summary to daily note |

### Agent programs (`agents/`)

Agent programs are markdown files that define autonomous loops. They are passed to an LLM
as the system prompt for an unattended run.

| Agent | Trigger | What it does |
|-------|---------|-------------|
| `discovery_program.md` | On-demand | Hypothesis → evaluate → iterate research loop |
| `architecture_program.md` | Weekly | Architecture drift review + proposals |
| `monitor_program.md` | Every 5 min (optional) | Health monitor → alerts to daily note |

### Knowledge seed (`knowledge-seed/`)

Baseline knowledge copied into `~/.claude/knowledge/` on install. Contains:
- 5 foundational QMP entries (deploy, database, debugging, feature ship, onboarding)
- Blank skill graph and decisions log templates

### Brain template (`brain-template/`)

Blank `.brain/` scaffold. `setup_brain.sh` copies this structure when initializing a new
project brain.

---

## Data flows

### Session start flow
```
Claude Code opens project
    → SessionStart hook fires
    → setup_brain.sh --check-only: scaffold .brain/ if missing
    → intelligence_brief_hook.py: read latest brief → print to session context
    → Claude reads BRAIN.md (auto-loaded from ~/.claude/)
    → Claude reads .brain/MEMORY.md + project_context.md
    → Session begins with full project context
```

### Intelligence update flow (every 6h)
```
Cron fires
    → project_intelligence.py runs for each registered project
        → reads git log, .brain/knowledge/, CLAUDE.md
        → calls LLM with project context
        → writes intelligence_brief_latest.md
    → global_intelligence_sweeper.py runs
        → reads all registered project briefs
        → synthesizes cross-project patterns
        → writes global_sweep_latest.md
```

### Knowledge capture flow
```
Claude completes a task
    → BRAIN.md memory logging rule triggers
    → Claude writes to appropriate .brain/knowledge/ file
    → .brain/MEMORY.md updated if new memory file added
    → nightly_review.sh (Stop hook): append session summary to daily note
```

---

## Two knowledge scopes

| Scope | Path | Contains | Shared? |
|-------|------|----------|---------|
| Global | `~/.claude/knowledge/` | Cross-project patterns, QMP, global skills, global decisions | Between all projects |
| Per-project | `<project>/.brain/knowledge/` | Project-specific context, local patterns, local decisions | Within one project |

Rule: if a pattern applies to more than one project, promote it to global.

---

## Extension points

### Adding a new intelligence script
1. Place script in `scripts/`
2. Reference in `install.sh` `SCRIPTS` array
3. Add cron entry in `install.sh` Step 6

### Adding a new agent program
1. Create `agents/my_program.md` following the existing agent format
2. Reference in `core/BRAIN.md` agent layer table

### Adding QMP seed entries
1. Create `knowledge-seed/qmp/qmp-NNN.md`
2. Add row to `knowledge-seed/qmp/_index.md`

### Per-project customization
Create `<project>/CLAUDE.md` — it overrides `BRAIN.md` for that project.
`BRAIN.md` is the default; `CLAUDE.md` is the override.

---

## Design decisions

| Decision | Rationale |
|----------|-----------|
| Markdown-only knowledge files | LLM-native, git-diffable, no database dependency |
| `~/.claude/` as global store | Co-located with Claude Code — zero extra config for users |
| SessionStart hook for briefs | Brief surfaces before any user message — context is always loaded |
| Cron for intelligence updates | Decoupled from sessions — brief is ready before session starts |
| Agent programs as markdown | Portable across LLM tools (Claude Code, Codex, Cursor) |
| PARA structure for knowledge | Proven system for managing project vs evergreen knowledge |
