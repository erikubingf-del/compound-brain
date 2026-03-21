# Activate Repo Design

**Date:** 2026-03-21
**Status:** Approved

## Goal

Turn `compound-brain` into a public GitHub project whose main product is an
actionable Claude skill that activates a repo, audits it, confirms strategic
direction, and makes that repo "alive" through memory, hooks, departments, and
bounded autonomous execution.

## Product Decisions

- The public entry point is a Claude-first `activate-repo` skill.
- The system is opt-in per repo; non-activated repos remain untouched.
- `~/.claude/` owns the shared runtime, cross-project memory, scheduler, QMD
  sync, and architecture-improvement loops.
- Each activated repo gets its own `.brain/` and `.claude/` control plane.
- Strategic confirmations are required only for project goal, department goals,
  and major architecture direction changes.
- Routine operational work remains autonomous once those strategic boundaries are
  set.
- A global GitHub architecture radar continuously learns from recent high-signal
  repos and feeds upgrades back into the shared orchestrator.

## System Shape

The system has two planes.

### Global plane

`~/.claude/` stores the shared orchestration runtime:

- hook runner and cron-backed LLM loops
- activation registry for alive repos
- cross-project knowledge, QMP, decisions, and skills
- QMD search/sync across activated repos
- probability and architecture-improvement primitives
- GitHub architecture radar for global learning

This plane is the upgrade surface. It evolves once and benefits every activated
repo.

### Repo plane

Every activated repo materializes local control surfaces:

- `.brain/` for project memory, daily/weekly notes, decisions, QMP, skills,
  audit artifacts, goals, and autonomy state
- `.claude/` for repo-specific hooks, scheduler config, and department
  definitions
- `CLAUDE.md` describing repo operating rules and the local brain contract

This keeps repo-specific goals, learning, and agent behavior inspectable and
portable with the codebase itself.

## Target File Layout

```text
~/.claude/
├── AGENTS.md
├── settings.json
├── registry/
│   └── activated-projects.json
├── hooks/
│   ├── session_start.py
│   ├── stop_capture.py
│   ├── llm_cron_runner.py
│   └── github_architecture_radar.py
├── orchestrator/
│   ├── activate_repo.py
│   ├── audit_repo.py
│   ├── goal_manager.py
│   ├── department_manager.py
│   ├── probability_engine.py
│   ├── qmd_sync.py
│   └── architecture_evolver.py
├── knowledge/
│   ├── daily/
│   ├── weekly/
│   ├── resources/
│   │   ├── architecture-radar.md
│   │   └── github-intelligence.md
│   ├── decisions/log.md
│   ├── qmp/
│   └── skills/
└── skills/
    └── activate-repo/
        └── SKILL.md
```

```text
<repo>/
├── CLAUDE.md
├── .claude/
│   ├── settings.local.json
│   ├── hooks/
│   │   ├── project_session_start.py
│   │   ├── project_stop.py
│   │   └── project_llm_cron.py
│   └── departments/
│       ├── architecture.md
│       ├── engineering.md
│       ├── product.md
│       └── research.md
└── .brain/
    ├── MEMORY.md
    ├── state/
    │   ├── goals.md
    │   ├── action-queue.md
    │   ├── audit-status.md
    │   └── autonomy-policy.md
    ├── memory/
    └── knowledge/
        ├── daily/
        ├── weekly/
        ├── projects/
        ├── areas/
        ├── resources/
        ├── qmp/
        ├── decisions/
        ├── skills/
        └── audits/
```

## Activation Lifecycle

Activation is a state machine, not a one-off install script.

### 1. Preflight

- Confirm the current directory is a git repo.
- Detect stack, package manager, CI files, docs, test commands, and existing
  local `.brain/` or `.claude/`.
- Register the repo in the global activation registry.
- Snapshot the starting state for audit and rollback awareness.

### 2. Initial audit

- Read repo structure, docs, and recent git history.
- Infer project goal, architecture, candidate departments, missing memory
  surfaces, risks, and high-confidence next actions.
- Write the results to `.brain/knowledge/audits/` and `.brain/state/`.

### 3. Strategic confirmation

Ask the user to confirm:

- the project goal
- the department set and department goals
- major architecture direction changes

Routine operational setup should not require confirmation.

### 4. Materialization

Create or update repo-local assets:

- `.brain/`
- `CLAUDE.md`
- `.claude/settings.local.json`
- `.claude/hooks/`
- `.claude/departments/*.md`
- local skills, QMP entries, goals, and autonomy policy

Update the shared runtime:

- global settings and hook wiring
- activated project registry
- cross-project memory/search links
- architecture-radar inputs

### 5. Go live

- start repo-local LLM hooks and cron-backed loops
- seed the first action queue
- mark the repo as alive in both the global registry and local state

### 6. Steady state

Session hooks surface:

- latest audit and intelligence brief
- active goals
- department priorities
- highest-confidence next actions

Scheduled loops continuously:

- re-audit on drift
- update memory, QMP, skills, and decisions
- refine department goals
- propose or execute bounded changes when gates pass

## Autonomous Loop Model

Each alive repo runs through multiple departments instead of one generalist
agent. The initial audit proposes the smallest useful department set for that
repo. The common default is:

- architecture
- engineering
- product
- research
- operations

Each department owns:

- a local goal
- allowed surfaces
- protected surfaces
- success signals
- a cadence for its LLM loop

Every department runs the same cycle:

1. Observe current repo state, logs, tests, and memory.
2. Orient against project goal and department goal.
3. Score candidate actions using confidence/probability.
4. Gate actions against strategic boundaries and validation requirements.
5. Execute scoped work in an isolated branch or worktree.
6. Learn from outcomes and update memory, skills, QMP, and confidence priors.

## Confidence and Action Ranking

Actions are ranked by a score derived from:

- goal alignment
- estimated impact
- probability of success
- urgency
- cost and risk
- evidence quality

Only the highest-confidence gated actions should move forward. The ranking and
reasoning must be logged to `.brain/state/action-queue.md`.

## Global GitHub Architecture Radar

The shared runtime must include a recurring loop that scans recent high-signal
GitHub repos and architecture patterns.

Its job is to:

- identify relevant repos and implementation patterns
- extract ideas useful to the orchestrator or alive repos
- compare those ideas against the current shared runtime
- score whether they improve architecture quality, execution confidence, or goal
  pursuit
- write ranked recommendations into global knowledge
- feed approved improvements back into the global runtime and repo-level upgrade
  proposals

The radar optimizes for better direction, not novelty. It should ignore trendy
patterns that do not materially improve the orchestrator.

## MVP Scope

### In scope

- global installer and shared runtime setup in `~/.claude/`
- Claude-first `activate-repo` skill and CLI/script entry point
- repo audit, strategic confirmation, and repo-local materialization
- repo-local `.brain/`, `.claude/`, hooks, departments, and action queues
- bounded autonomous execution in isolated branches or worktrees
- memory/QMP/skills/decisions updates
- global GitHub architecture radar and architecture knowledge updates
- documentation and examples for repo activation

### Out of scope

- full Codex/Cursor parity beyond file compatibility
- fully general code execution across every stack
- automatic merge to main
- hosted control plane or cloud sync
- external system mutations by default

## Success Criteria

- Running the activation skill in a repo creates the shared runtime if needed
  and makes that repo alive.
- Activated repos receive a usable audit, confirmed goals, department goals,
  local memory, local hooks, and scheduled improvement loops.
- The next Claude session in an activated repo starts with an informed brief and
  ranked next actions.
- The global orchestrator improves itself through the GitHub architecture radar
  and cross-project learning.
