# compound-brain

**An autonomous, self-improving AI second brain for software projects.**

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

compound-brain is a **meta-layer for software projects** that makes every repo self-aware, self-improving, and probability-driven.

It combines:
- **PARA knowledge system** (Tiago Forte) — Projects, Areas, Resources, Archives
- **QMP library** — reusable Question-Model-Process intelligence patterns
- **Autonomous agent loops** — discovery, monitoring, auditing, architecture
- **Cron + Claude Code hooks** — intelligence runs on schedule, surfaces at session start
- **Probability engine** — agents rank next actions by expected outcome value
- **GitHub intelligence** — weekly sweep of external repos to keep architecture current

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

# Add a project brain to any existing repo
bash scripts/setup_brain.sh /path/to/your/project "My Project Description"

# Verify
python3 scripts/project_intelligence.py --project-dir /path/to/your/project --dry-run
```

---

## Architecture layers

| Layer | What it does | How it runs |
|---|---|---|
| **Global brain** | Cross-project PARA memory, decisions, skills | Always present at `~/.claude/knowledge/` |
| **Project brain** | Per-project `.brain/` with PARA + memory | Created on first use via `setup_brain.sh` |
| **Intelligence cron** | LLM briefings every 6h, per-project and global | System crontab |
| **Session hooks** | Pre-computed briefs surface at session start | Claude Code `settings.json` |
| **Auditor** | Deep initial audit of new projects | Runs once on project registration |
| **Discovery loop** | Autonomous candidate generation + evaluation | `autoresearch` skill or cron |
| **Monitor loop** | Live gate tracking, collapse detection | 5-min polling, cron |
| **Architecture guardian** | Keeps system architecture current | Weekly cron |
| **GitHub sweep** | External intelligence from GitHub | Weekly cron |
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

### 1. Install global brain

```bash
bash install.sh
```

This sets up `~/.claude/knowledge/`, installs hooks in `settings.json`, seeds QMP library, and adds cron jobs.

### 2. Add your project

```bash
bash scripts/setup_brain.sh /path/to/my-project "Description of what the project does"
```

This creates `.brain/` in your project with scaffolded memory + knowledge files.

### 3. Run the initial audit

```bash
# Opens an agent session to audit your project
python3 scripts/project_auditor.py --project-dir /path/to/my-project
```

The auditor reads all code, docs, and history, then writes a structured analysis to `.brain/knowledge/`.

### 4. Start a Claude Code session

```bash
cd /path/to/my-project
claude
```

The hooks run automatically at session start. If an intelligence brief exists, it surfaces immediately. The auditor's findings are in context. The system knows where you left off.

---

## Cron schedule

After `install.sh`, the following cron jobs are active:

| Schedule | Job | Output |
|---|---|---|
| Every 6h `:00` | Per-project intelligence brief (any registered project) | `.brain/daily/` |
| Every 6h `:30` | Global cross-project sweep | `~/.claude/knowledge/daily/` |
| Weekly Sunday | GitHub intelligence sweep | `~/.claude/knowledge/resources/github-intel.md` |
| Weekly Sunday | Architecture guardian review | `~/.claude/knowledge/areas/` |

---

## Claude Code hook integration

At every session start, the following run automatically:
1. Check if `.brain/` exists — create if missing
2. Run project health check
3. Load latest AI intelligence brief
4. Surface findings to the conversation

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
