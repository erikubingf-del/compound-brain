# compound-brain

**A shared orchestration layer for Claude Code and Codex.**

`compound-brain` installs one global brain into `~/.claude` and a managed
Codex adapter into `~/.codex/AGENTS.md`, so both tools operate with the same
memory model, repo language, and runtime rules.

After install, Claude and Codex should:
- search and write against the same PARA/QMP-style knowledge system
- read the same repo control surfaces: `CLAUDE.md`, `.brain/`, and `.claude/`
- follow the same preview, prepare, activate lifecycle
- promote reusable learnings through the same global review path

That gives you one orchestrator across tools, and one living project brain per
activated repo instead of parallel Claude/Codex memory systems.

Repos then move through a strict lifecycle:

1. `observe` — detect the repo, read it, do not write repo files
2. `preview` — store a global read-only recommendation
3. `prepare-brain` — write `CLAUDE.md`, `.brain/`, and `.codex/AGENTS.md`
4. `activate-repo` — add `.claude/`, departments, approvals, hooks, crons, and
   bounded autonomy

## What installs globally

The global install is the cross-project orchestrator. It is responsible for:

- overall memory architecture in `~/.claude/`
- shared logs, skills, QMP, decisions, and retrieval behavior
- repo preview cache for non-activated projects
- promotion inbox and scheduled review for cross-project learnings
- architecture radar and recurring improvement loops
- a managed Codex bootstrap so Codex speaks the same operating language as
  Claude

This layer should improve itself over time without depending on any single
project repo.

## Core model

- Global brain in `~/.claude/`
  - shared memory architecture
  - preview cache for non-activated repos
  - promotion inbox for cross-project learnings
  - architecture radar and scheduled review loops
- Repo brain in `.brain/`
  - project memory, goals, logs, skills, QMP, approvals, autoresearch
- Repo runtime in `.claude/`
  - created only after activation
  - department contracts, local settings, hook wrappers
- Codex adapter in `.codex/AGENTS.md`
  - reads the same repo control plane as Claude
  - does not create a second repo runtime

## What activated repos become

An activated repo is treated like a small company run by a bounded
orchestrator:

- departments are created from the repo shape and project goal
- each department gets contracts, owned surfaces, state, and memory
- hooks and cron-driven loops keep reviewing, logging, and improving work
- project-specific skills, QMP, and decisions accumulate in `.brain/`
- strategic changes still go through approvals instead of silent drift

## Why this shape

- Non-activated repos stay read-only.
- Prepared repos get static project memory, but no autonomy.
- Activated repos get departments, logs, approvals, and continuous bounded improvement.
- Cross-project learnings go to a global inbox instead of mutating global memory directly.
- `compound-brain` itself is the self-hosting exception: always prepared, always activated, and improved by its own loops against a fixed evaluator.

## Quick start

```bash
git clone https://github.com/your-username/compound-brain
cd compound-brain
bash install.sh
```

Read-only preview for a repo:

```bash
python3 ~/.claude/scripts/activate_repo.py --project-dir /path/to/repo --check-only
```

Prepare static project memory:

```bash
python3 ~/.claude/scripts/prepare_brain.py /path/to/repo
```

Activate full repo autonomy:

```bash
python3 ~/.claude/scripts/activate_repo.py --project-dir /path/to/repo
```

## What activation creates

`prepare-brain` writes:
- `CLAUDE.md`
- `.brain/`
- `.codex/AGENTS.md`

`activate-repo` adds:
- `.claude/settings.local.json`
- `.claude/hooks/*.py`
- `.claude/departments/*.md`
- `.brain/state/approval-state.json`
- `.brain/state/departments/*.json`
- `.brain/autoresearch/program.md`

## Department runtime

Activated repos get a bounded department-cycle runtime:

- `architecture`
- `engineering`
- `product`
- `research`

Each department has:
- a contract in `.claude/departments/`
- state in `.brain/state/departments/`
- memory in `.brain/knowledge/departments/`

The runtime always gates before acting:
- approvals first
- owned/protected surfaces
- bounded action selection
- logged result

Activated repos also get real event loops:
- `SessionStart` refreshes audit, intelligence brief, and ranked actions
- `Stop` refreshes project state and updates self-hosting scorecards when relevant
- repo cron refreshes audit and briefs, then runs department and autoresearch cycles

## Heartbeats

The runtime now records and reviews its own operational health:

- per-repo heartbeat state under `~/.claude/registry/runtime-heartbeats/`
- per-repo lockfiles under `~/.claude/registry/runtime-locks/`
- failure backoff for cron-driven retries
- watchdog report under `~/.claude/knowledge/resources/runtime-heartbeats.md`

This means scheduled loops are not just configured. They leave evidence of the
last run, last success, next due time, consecutive failures, and missed-heartbeat
status.

## Autoresearch

Autoresearch is fixed-evaluator only.

It runs from:
- `.brain/autoresearch/program.md`
- `.brain/autoresearch/baseline.json`
- `.brain/autoresearch/results.jsonl`
- `.brain/autoresearch/queue.md`

Without explicit approval and a valid program contract, it does not run.
When enabled, repo cron now executes the evaluator, records baseline and result
artifacts, and makes a bounded keep/discard decision from the configured rule.

## Self-hosting

`compound-brain` is the source repo for the orchestrator and should auto-improve
through its own hooks and cron loops. Those loops are constrained by:

- `.brain/architecture/evaluator.md`
- `.brain/architecture/scorecard.json`

The evaluator is fixed unless explicitly approved to change.

## Current status

Implemented in the current MVP branch:
- global preview cache
- `prepare-brain`
- activation approvals
- department contracts and state
- bounded department-cycle runtime
- shared project runtime event engine for session start, stop, and cron autoimprovement
- heartbeat ledger, lockfiles, retry backoff, and watchdog reporting for activated repos
- evaluator-backed autoresearch execution with keep/discard results
- local skill promotion, global promotion inbox, scheduled review, and approved
  promotion application into canonical global knowledge
- self-hosting evaluator surfaces plus scorecard automation
- managed Codex bootstrap and shared nightly review wrapper

Still evolving:
- deeper execution logic inside department cycles
- worktree-isolated experiment mutations beyond bounded evaluator runs
- richer promotion authoring from departments into global QMP/skills/decisions
