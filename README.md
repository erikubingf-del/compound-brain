# compound-brain

**A shared orchestration layer for Claude Code and Codex.**

`compound-brain` installs one global brain into `~/.claude` and a managed
Codex adapter into `~/.codex/AGENTS.md`, so both tools operate with the same
memory model, repo language, and runtime rules.

## Core Principle

`compound-brain` exists to turn LLMs from reactive responders into proactive,
memory-driven project operators.

That means the runtime should:

- wake on hooks and cron heartbeats instead of waiting for perfect prompts
- preload the smallest correct context from `CLAUDE.md`, `.brain/`, `.claude/`,
  QMP, logs, and approvals
- decide which department should lead and which supporting departments matter
- recommend the next best bounded action instead of only answering the last
  question asked
- act only when approvals, trust, protected surfaces, and evaluators allow it

The goal is not unlimited autonomy. The goal is evidence-weighted,
high-confidence progress toward the repo's objective.

After install, Claude and Codex should:
- search and write against the same PARA/QMP-style knowledge system
- read the same repo control surfaces: `CLAUDE.md`, `.brain/`, and `.claude/`
- follow the same preview, prepare, activate lifecycle
- promote reusable learnings through the same global review path

That gives you one orchestrator across tools, and one living project brain per
activated repo instead of parallel Claude/Codex memory systems.

## Credibility Contract

`compound-brain` should feel active and useful, but it should stay credible.

So the project makes these stronger claims:

- hooks and cron jobs are wake-up mechanisms into one shared runtime, not
  separate agent brains
- every autonomous step should be traceable through state files, logs,
  approvals, evaluator results, or heartbeat records
- activated repos should recommend what happens next before they attempt to act
- departments may be proactive, but they stay bounded by owned surfaces,
  approvals, and current autonomy depth
- confidence is evidence-weighted, not mystical certainty or oracle behavior

Repos then move through a strict lifecycle:

1. `observe` — detect the repo, read it, do not write repo files
2. `preview` — store a global read-only recommendation
3. `prepare-brain` — write `CLAUDE.md`, `.brain/`, and `.codex/AGENTS.md`
4. `activate-repo` — add `.claude/`, departments, approvals, hooks, crons, and
   bounded autonomy

## What installs globally

The global install is the cross-project orchestrator. It is responsible for:

- overall memory architecture in `~/.claude/`
- global autonomy-depth policy in `~/.claude/policy/`
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

Activated repos should therefore feel less like a chat session and more like a
disciplined operating company:

- `SessionStart` wakes the repo brain, refreshes context, and surfaces the best
  next move
- `Stop` compresses learning into logs, skills, and decisions
- heartbeat cron runs keep departments reviewing, researching, and maintaining
  progress between sessions
- the runtime should proactively say what should happen next, which department
  is active, what is blocked, and why

## Community growth model

The repo should improve with the community through bounded contribution lanes,
not by letting every contribution modify the orchestration kernel directly.

Community-first lanes live in:

- `community/skills/`
- `community/departments/`
- `community/source-packs/`
- `community/evaluators/`
- `community/case-studies/`
- `community/benchmarks/`
- `community/promotions/`

This lets people contribute:

- better skills for specific repo types
- department operating models
- approved source packs for safe external research
- fixed evaluators for bounded autonomy
- case studies showing real activated-repo outcomes
- benchmarks that prove whether changes actually help

Maintainers can then review and promote the best artifacts into templates,
knowledge seeds, or runtime defaults.

## Why this shape

- Non-activated repos stay read-only.
- Prepared repos get static project memory, but no autonomy.
- Activated repos get departments, logs, approvals, and continuous bounded improvement.
- Cross-project learnings go to a global inbox instead of mutating global memory directly.
- `compound-brain` itself is the self-hosting exception: always prepared, always activated, and improved by its own loops against a fixed evaluator.

## Quick start

```bash
git clone https://github.com/erikubingf-del/compound-brain
cd compound-brain
bash install.sh
```

Then activate any repo you own:

```bash
# Step 1 — preview (read-only, nothing written)
python3 ~/.claude/scripts/activate_repo.py --project-dir /path/to/repo --check-only
# Prints: detected stack, recommended goal, suggested departments
# You see this, nothing changes on disk

# Step 2 — prepare (writes .brain/ + CLAUDE.md, no autonomy yet)
python3 ~/.claude/scripts/prepare_brain.py /path/to/repo
# Creates .brain/memory/, .brain/knowledge/, CLAUDE.md, .codex/AGENTS.md
# Safe to commit to git

# Step 3 — activate (adds .claude/, departments, hooks, autonomy-depth state)
python3 ~/.claude/scripts/activate_repo.py --project-dir /path/to/repo
# Confirms goal and departments with you before writing
# After this: open the repo in Claude Code or Codex and the runtime is live

# Step 4 — check status any time
python3 ~/.claude/scripts/activate_repo.py --project-dir /path/to/repo --check-only
# Shows: current depth, trust score, active skills, pending approvals
```

See [`examples/activate-repo-demo.md`](examples/activate-repo-demo.md) for a
walkthrough with expected output at each step.

For a deeper explanation of what departments, autonomy-depth, and skills do
once activated, see [`GETTING-STARTED.md`](GETTING-STARTED.md).

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
- `.brain/state/autonomy-depth.json`
- `.brain/state/runtime-governor.json`
- `.brain/state/runtime-packet.json`
- `.brain/state/context-snapshot.json`
- `.brain/state/departments/*.json`
- `.brain/state/skills.json`
- `.brain/autoresearch/program.md`

Before goals are confirmed, activation now also writes a recommendation into the
approval state and prints it in the activation output. That recommendation can:

- propose a cleaner `project_goal` based on repo reality
- propose aligning department names to an existing repo-native structure
- ask for confirmation before those strategic changes are applied

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
- an approved source pack in `.brain/knowledge/departments/<department>-sources.md`
- a skill-shopping state file in `.brain/state/departments/<department>-shopping.json`

The runtime always gates before acting:
- approvals first
- owned/protected surfaces
- bounded action selection
- logged result

The runtime should not wait passively for the user to reconstruct project
context every session. It should wake into the repo's current reality and
recommend the next highest-confidence move from memory, logs, QMP, skills,
approvals, and department state.

Activated repos also get real event loops:
- `SessionStart` refreshes audit, intelligence brief, and ranked actions
- `Stop` refreshes project state and updates self-hosting scorecards when relevant
- repo cron refreshes audit and briefs, then runs department and autoresearch cycles

## Autonomy Depth Governor

Activated repos now run with an explicit depth governor instead of one fixed
autonomy level.

Global policy lives in:

- `~/.claude/policy/autonomy-depth.json`
- `~/.claude/policy/required-context.json`

Per-repo runtime state lives in:

- `.brain/state/autonomy-depth.json`
- `.brain/state/runtime-governor.json`
- `.brain/state/runtime-packet.json`
- `.brain/state/context-snapshot.json`
- `.brain/state/department-agreement.json`
- `.brain/state/department-health.json`

Depth ladder:

- `0` preview-only
- `1` memory-only
- `2` bounded planning
- `3` bounded execution
- `4` evaluator-backed experiments
- `5` high autonomy

The runtime now:

1. loads user policy and repo depth
2. pre-hydrates deterministic repo state like skills and ranked actions
3. builds a fail-closed context snapshot from required files
4. computes cross-department agreement before execution lanes are opened
5. computes a trust score from approvals, heartbeat health, skill coverage, department health, validation signals, and agreement state
6. writes a compact runtime packet for Claude and Codex
7. raises, lowers, or freezes depth from trust history, healthy streaks, and department objections

This keeps repo autonomy adaptive per user and per repo without letting the
runtime exceed the user’s declared ceiling.

## Repo skill matching

Every activated repo gets automatic skill discovery — no manual configuration.

On session start and cron, the runtime reads the project's observable signals
(file extensions, package dependencies, language markers) and scores every
available skill against them. Skills match by their declared `Trigger Signals`,
not by hardcoded repo names.

```
session-start (any repo)
  → skill-gap-detector evaluator (10s, file scan only)
  → scores skills by Trigger Signals vs project signals
  → missing match → added to recommended[], human notified
  → pass → silent

daily cron
  → skill-gap-detector (60s, includes HTTP)
  → fetches skill-discovery-sources pack (registries + stack refs)
  → new skill found with score ≥ 2 → proposed via promotion inbox
  → existing skill stale → refresh diff proposed via promotion inbox
  → human approves → skill enters active[]
```

See [`community/skills/RUNTIME.md`](community/skills/RUNTIME.md) for the full
loop and budget rules.

### Skill scopes

Skills exist at three scopes, searched in order:

| Scope | Location | Use for |
|-------|----------|---------|
| **Repo-local** | `.claude/skills/` or `.brain/knowledge/skills/` | Repo-specific overrides |
| **Personal global** | `~/.claude/skills/` | Your private skills, all your repos |
| **Org/team** | Private Git repo, added to source pack | Shared across team, not public |
| **Community** | `community/skills/` in this repo | Public, peer-reviewed |

For org/team sharing, see [`community/skills/SHARING.md`](community/skills/SHARING.md).

### Skill state files

- `.brain/state/skills.json` — active, recommended, stale, missing per repo
- `.brain/knowledge/skills/skill-graph.md` — capability map
- `.brain/knowledge/skills/patterns/*.md` — materialized skill patterns
- `.brain/state/source-pack-cache.json` — last-fetched timestamps per source

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
- `~/.claude/policy/ralph-policy.json`

The evaluator is fixed unless explicitly approved to change.

For self-hosting implementation lanes, `compound-brain` can now auto-route
eligible cron work into a one-story Ralph loop instead of the default bounded
cron executor. That routing is narrow on purpose:

- only `compound-brain` uses it automatically
- only `cron` can trigger it
- current depth must be `4+`
- trust score and healthy streak must clear the Ralph policy threshold
- no strategic approvals can be pending
- architecture or operations objections block it
- only eligible action categories like `feature`, `debt`, and `research` can route

When those gates pass, the runtime creates or refreshes
`.agents/tasks/prd-compound-brain-auto.json`, runs one Ralph iteration, and
writes `.brain/state/ralph-state.json` so the repo has a durable record of what
Ralph did.

## Current status

Implemented in the current MVP branch:
- global preview cache
- `prepare-brain`
- activation approvals
- department contracts and state
- bounded department-cycle runtime
- shared project runtime event engine for session start, stop, and cron autoimprovement
- heartbeat ledger, lockfiles, retry backoff, and watchdog reporting for activated repos
- repo-aware skill matching across local, global, and approved external skill sources
- autonomy-depth policy, fail-closed context snapshots, runtime packets, cross-department arbitration, and trust-governed depth state with history
- evaluator-backed autoresearch execution with keep/discard results
- local skill promotion, global promotion inbox, scheduled review, and approved
  promotion application into canonical global knowledge
- self-hosting evaluator surfaces plus scorecard automation
- self-hosting Ralph auto-routing for eligible `compound-brain` cron lanes
- managed Codex bootstrap and shared nightly review wrapper

## Feature status

| Feature | Status | Notes |
|---------|--------|-------|
| Lifecycle (preview → prepare → activate) | Stable | Full CLI workflow |
| Global brain (`~/.claude/`) | Stable | PARA, QMP, skills, decisions |
| Repo preview cache | Stable | Read-only, no disk writes |
| Static brain preparation | Stable | `.brain/` + `CLAUDE.md` |
| Activation + approval gates | Stable | Goal/dept confirmation before writing |
| Department runtime | MVP | Bounded queue handling; works, not rich |
| Autonomy-depth governor | Stable | Auto-raise/lower with trust scoring |
| Fixed-evaluator autoresearch | Stable | Approval-gated, keep/discard |
| Skill discovery + materialization | Stable | Auto-detects by stack signals |
| Generic skill-gap-detector | Stable | Session-start + cron, any repo type |
| Skill-discovery-sources pack | Stable | Registries + stack-conditional refs |
| Heartbeat + watchdog | Stable | Retry backoff, missed-heartbeat alerts |
| Promotion inbox + review | Stable | Repo → global review → approved apply |
| Ralph auto-routing | Stable | Self-hosting (`compound-brain`) only |
| Codex bootstrap | Stable | Shared control plane via same files |
| Self-hosting evaluator | Stable | Locked contract + scorecard |
| Community skill examples | Growing | 1 example (ui-master); more welcome |
| Deeper department execution | Planned | Richer action logic per dept cycle |
| Worktree-isolated mutations | Planned | Pattern described; no code yet |
| Full Codex execution parity | Partial | Bootstrap works; deep loops TBD |
| Real-world case studies | Wanted | See `community/case-studies/TEMPLATE.md` |

The system is safe to use today at depths 2–3 for any activated repo.
Depths 4–5 (evaluator-backed experiments, high autonomy) require autoresearch
enablement and a validated evaluator contract.

Still evolving:
- richer execution logic inside department cycles
- worktree-isolated experiment mutations beyond bounded evaluator runs
- richer promotion authoring from departments into global QMP/skills/decisions
