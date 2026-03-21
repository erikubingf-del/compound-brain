# compound-brain

**A global AI orchestrator with explicit repo activation.**

`compound-brain` installs a shared brain once into `~/.claude`, then manages
repos through a strict lifecycle:

1. `observe` — detect the repo, read it, do not write repo files
2. `preview` — store a global read-only recommendation
3. `prepare-brain` — write `CLAUDE.md`, `.brain/`, and `.codex/AGENTS.md`
4. `activate-repo` — add `.claude/`, departments, approvals, hooks, crons, and bounded autonomy

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

## Autoresearch

Autoresearch is fixed-evaluator only.

It runs from:
- `.brain/autoresearch/program.md`
- `.brain/autoresearch/baseline.json`
- `.brain/autoresearch/results.jsonl`
- `.brain/autoresearch/queue.md`

Without explicit approval and a valid program contract, it does not run.

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
- autoresearch program parsing and runner skeleton
- local skill promotion and global promotion inbox
- self-hosting evaluator surfaces

Still evolving:
- deeper execution logic inside department cycles
- richer keep/discard experiment execution
- stronger self-hosting canary and scorecard automation
