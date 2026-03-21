# compound-brain

**An activation-first, self-improving AI second brain for software repos.**

Every project gets a living intelligence layer that audits, monitors, learns, and pushes agents toward the highest-probability path to success — automatically, around the clock.

```
┌─────────────────────────────────────────────────────────┐
│                   Global Orchestrator                   │
│  (cross-project memory, weekly GitHub sweep, evolution) │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
    ┌──────────▼──────────┐    ┌──────────▼──────────┐
    │  Project Brain      │    │  Project Brain      │
    │  .brain/            │    │  .brain/            │
    │  ├── MEMORY.md      │    │  ├── MEMORY.md      │
    │  ├── memory/        │    │  ├── memory/        │
    │  └── knowledge/     │    │  └── knowledge/     │
    │      ├── daily/     │    │      ├── daily/     │
    │      ├── decisions/ │    │      ├── decisions/ │
    │      ├── skills/    │    │      ├── qmp/       │
    │      └── qmp/       │    │      └── skills/    │
    └──────────┬──────────┘    └─────────────────────┘
               │
    ┌──────────▼──────────────────────────────────────┐
    │              Agent Layers                        │
    │                                                  │
    │  Auditor → Discovery → Monitor → Architecture   │
    │     ↓           ↓         ↓            ↓        │
    │  initial    autoresearch  live        system     │
    │  audit      loop         monitoring  evolution   │
    └─────────────────────────────────────────────────┘
```

---

## What this is

compound-brain is an **activation-first meta-layer for software projects**. You
run one command inside a repo, it scaffolds the repo's memory and local control
plane, and that repo becomes goal-driven, auditable, and continuously improved.

It combines:
- **PARA knowledge system** (Tiago Forte) — Projects, Areas, Resources, Archives
- **QMP library** — reusable Question-Model-Process intelligence patterns
- **Autonomous agent loops** — discovery, monitoring, auditing, architecture
- **Cron + Claude Code hooks** — intelligence runs on schedule, surfaces at session start
- **Probability engine** — agents rank next actions by expected outcome value
- **GitHub architecture radar** — weekly sweep of external repos ranked by architectural usefulness

When you start a Claude Code or Codex session, pre-computed AI analysis is waiting for you. When you're not working, agents are still learning.

---

## Core concepts

### Compound intelligence
Every session deposits knowledge into the system. The system becomes more valuable over time — not just a log, but a compounding intelligence layer that learns what works.

### Probability-driven actions
Agents don't just react. They score candidate actions by expected value (impact × probability of success × urgency) and push toward the highest-probability path for the project's goal.

### Two scopes, one operating model
- **Global** (`~/.claude/knowledge/`) — cross-project patterns, skills, decisions
- **Per-project** (`.brain/`) — project-specific context, isolated learning

### Autonomous evolution
The system runs without human input via cron jobs and Claude Code hooks. Agents audit, discover, monitor, and improve — then surface findings at the next session start.

---

## Quick install

```bash
# Clone and install
git clone https://github.com/yourusername/compound-brain
cd compound-brain
bash install.sh

# Activate any existing repo
python3 ~/.claude/scripts/activate_repo.py --project-dir /path/to/your/project

# Verify
python3 scripts/activate_repo.py --project-dir /path/to/your/project --check-only
```

---

## Architecture layers

| Layer | What it does | How it runs |
|---|---|---|
| **Global brain** | Cross-project PARA memory, decisions, skills | Always present at `~/.claude/knowledge/` |
| **Project brain** | Per-project `.brain/` with PARA + memory | Created during repo activation |
| **Repo-local runtime** | `.claude/` hooks and departments | Created during repo activation |
| **Intelligence cron** | LLM briefings every 6h, per-project and global | System crontab |
| **Session hooks** | Pre-computed briefs surface at session start | Claude Code `settings.json` |
| **Auditor** | Deep initial audit of new projects | Runs once on project registration |
| **Discovery loop** | Autonomous candidate generation + evaluation | `autoresearch` skill or cron |
| **Monitor loop** | Live gate tracking, collapse detection | 5-min polling, cron |
| **Architecture guardian** | Keeps system architecture current | Weekly cron |
| **GitHub architecture radar** | External repos ranked by architecture and goal fit | Weekly cron |
| **Probability engine** | Ranks next actions by expected value | Called by all agents |

---

## Directory structure

```
~/.claude/                              ← Global brain (installed by install.sh)
├── BRAIN.md                           ← Master operating instructions
├── intelligence_projects.json         ← Project registry
├── settings.json                      ← Claude Code hooks
├── knowledge/                         ← PARA knowledge base
│   ├── daily/                         ← Daily capture
│   ├── weekly/                        ← Weekly synthesis
│   ├── projects/                      ← Active project files
│   ├── areas/                         ← Ongoing responsibilities
│   ├── resources/                     ← Reusable patterns
│   ├── archives/                      ← Completed work
│   ├── decisions/log.md               ← Decision history
│   ├── skills/skill-graph.md          ← Skill capability map
│   └── qmp/                           ← QMP library (reusable intelligence)
└── scripts/                           ← Automation scripts

<project>/
├── CLAUDE.md                          ← Project-specific instructions
└── .brain/                            ← Project brain
    ├── MEMORY.md                      ← Memory index
    ├── memory/                        ← Session state + profiles
    └── knowledge/                     ← Per-project PARA
```

---

## Agent system

Each project gets a stack of specialized agents that operate in sequence:

```
1. Auditor      — runs once on first setup
                  maps codebase, reads docs, understands architecture
                  writes audit report to .brain/knowledge/

2. Discoverer   — runs via autoresearch loop
                  proposes new features/fixes/patterns
                  evaluates against fixed criteria
                  writes board proposals when gates pass

3. Monitor      — runs every 5 minutes
                  tracks live metrics (test pass rate, error rate, gate progress)
                  flags anomalies for board attention

4. Architect    — runs weekly
                  reviews system architecture vs best practices
                  proposes improvements to core files
                  keeps BRAIN.md and orchestrator files current

5. Intelligence — runs every 6h
                  collects state, calls LLM, writes briefing
                  surfaces at next session start via hook
```

---

## Probability engine

Agents don't act randomly. Before taking action, every agent scores candidate actions:

```
Expected Value = Impact × P(success) × Urgency / Cost

Impact:    What does this move toward project goal?
P(success): How likely does this work given current state?
Urgency:   How bad does it get if delayed?
Cost:      How much complexity, time, or risk does this add?
```

Actions are ranked. Agents pick from the top 3. The reasoning is logged. Over time, outcomes validate the scoring model and improve future estimates.

---

## Getting started

### 1. Install the shared runtime

```bash
bash install.sh
```

This sets up `~/.claude/knowledge/`, installs shared hooks in `settings.json`,
seeds the knowledge base, installs activation scripts, and adds cron jobs.

### 2. Activate your project

```bash
python3 ~/.claude/scripts/activate_repo.py --project-dir /path/to/my-project
```

This runs preflight, infers starter departments, scaffolds `.brain/`,
materializes repo-local `.claude/`, and registers the repo with the shared
runtime.

### 3. Review strategic confirmations

Confirm:
- project goal
- department goals
- major architecture changes

### 4. Start a Claude Code session

```bash
cd /path/to/my-project
claude
```

The shared runtime and repo-local hooks run automatically at session start. If
an intelligence brief exists, it surfaces immediately. Ranked next actions are
available in `.brain/state/action-queue.md` and `.claude/departments/*.md`.

---

## Cron schedule

After `install.sh`, the following cron jobs are active:

| Schedule | Job | Output |
|---|---|---|
| Every 6h `:00` | Repo-local LLM cron for activated projects | `.claude/hooks/` + `.brain/state/` |
| Every 6h `:30` | Global cross-project sweep | `~/.claude/knowledge/daily/` |
| Weekly Sunday | GitHub architecture radar | `~/.claude/knowledge/resources/architecture-radar.md` |
| Weekly Sunday | Architecture guardian review | `~/.claude/knowledge/areas/` |

---

## Claude Code hook integration

At every session start, the following run automatically:
1. Check activation state for the repo
2. Load latest AI intelligence brief
3. Read repo-local hooks and department context
4. Surface ranked next actions to the conversation

At every session end (via `Stop` hook):
- Capture session summary to daily note
- Update project MEMORY.md
- Log decisions to decision log

---

## Philosophy

This system is built on three beliefs:

1. **Knowledge should compound.** Every session should make future sessions more effective — not start from scratch.

2. **Agents should be direction-aware.** An agent that knows the destination can make better micro-decisions than one executing a checklist.

3. **The system should improve itself.** Autonomy without self-improvement degrades. The architecture guardian, weekly sweeps, and QMP library ensure the system gets smarter over time.

---

## License

MIT

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

To add a QMP entry: see [knowledge-seed/qmp/](knowledge-seed/qmp/).
To propose a new agent layer: open an issue with the template in [docs/AGENT_PROPOSAL.md](docs/AGENT_PROPOSAL.md).
