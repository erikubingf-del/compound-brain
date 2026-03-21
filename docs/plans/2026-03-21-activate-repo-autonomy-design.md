# Activate Repo Autonomy Layer Design

**Date:** 2026-03-21
**Status:** Approved

## Goal

Extend `compound-brain` into a self-hosting orchestrator that installs a global
brain once, observes every repo read-only by default, and only enables
project-local autonomy after explicit `prepare-brain` and `activate-repo`
actions.

## Product Decisions

- The global brain installs into `~/.claude` and upgrades the overall
  orchestrator for every repo and every session.
- Ordinary repos follow a four-state lifecycle:
  `observe -> preview -> prepare -> activate`.
- Non-activated repos remain read-only and get only a global preview cache.
- `prepare-brain` writes project memory and a Codex adapter, but no local
  runtime.
- `activate-repo` turns on repo-local `.claude/`, departments, approvals,
  hooks, crons, logs, skills, and bounded autonomy.
- `.brain/` and `.claude/` are the only canonical repo-level control planes.
- Cross-project learnings never rewrite global PARA/QMP/skills directly; they
  go to a global promotion inbox reviewed on the scheduled global loop.
- `compound-brain` itself is a self-hosting exception: always prepared, always
  activated, and continuously self-improving through its own hooks/crons.
- `compound-brain` evolves against a fixed architecture evaluator that cannot be
  rewritten without explicit approval.

## System Shape

The system has two planes.

### Global plane

`~/.claude/` owns cross-project orchestration:

- shared hook runtime and cron dispatcher
- global PARA/QMP/skills/decisions architecture
- repo preview cache for non-activated repos
- activation registry for prepared and activated repos
- GitHub architecture radar and weekly research
- promotion inbox for candidate cross-project learnings
- shared engine used by both Claude hooks and Codex automations

The global plane evolves continuously, but it stays stable and reviewable. One
project cannot silently mutate the global operating model.

### Repo plane

A repo only gets a local plane after explicit user intent:

- `prepare-brain` creates `CLAUDE.md`, `.brain/`, and `.codex/AGENTS.md`
- `activate-repo` adds `.claude/`, departments, approvals, hooks, cron wiring,
  objectives, logs, skill evolution, and autoresearch when eligible

Project-specific intelligence lives in the repo only after activation.

## Repo Lifecycle

### 1. Observe

The global brain detects a repo and reads it without writing repo files.

Allowed behavior:

- identify stack, docs, tests, CI, and current git state
- infer whether the repo is first-seen or materially changed
- decide whether a preview refresh is due

No repo-local writes occur in this state.

### 2. Preview

The global brain runs a read-only audit for a non-activated repo and stores the
result in a global cache such as:

- `~/.claude/registry/repo-previews.json`
- `~/.claude/knowledge/projects/previews/<repo>.md`

The cached preview may include:

- inferred project goal
- proposed departments
- main risks
- suggested next actions
- confidence
- last commit seen
- dismissal state

The orchestrator may recommend activation when confidence is high, but it must
not write repo files.

Preview cadence:

- run on first-seen repo
- rerun when the repo changes materially
- otherwise refresh on cooldown, such as weekly

### 3. Prepare

`prepare-brain` is the explicit action that installs project memory without
enabling autonomy.

It writes only:

- `CLAUDE.md`
- `.brain/`
- `.codex/AGENTS.md`

It does not write:

- `.claude/`
- departments
- local hooks/crons
- local autonomy loops

Prepared repos remain static until activation. The global brain may still keep a
preview cache, but it does not append ongoing project memory into `.brain/`
before activation.

### 4. Activate

`activate-repo` turns a prepared repo into an alive repo.

Activation adds:

- `.claude/settings.local.json`
- `.claude/hooks/`
- `.claude/departments/*.md`
- `.brain/state/approval-state.json`
- `.brain/state/departments/*.json`
- project objectives, action queues, logs, and skill evolution surfaces
- autoresearch program and results state when the repo qualifies

From this point on, project-specific memory, logs, skills, approvals, and
bounded autonomous improvement all happen inside that repo.

## Shared Control Plane

Every activated repo has one canonical local operating surface:

- `CLAUDE.md` for project instructions
- `.brain/` for memory, goals, approvals, decisions, skills, QMP, logs,
  evaluator state, and autoresearch
- `.claude/` for executable control-plane assets such as hook wrappers, local
  settings, and department specs

Codex compatibility is a thin adapter, not a second runtime:

- `.codex/AGENTS.md` instructs Codex to read `CLAUDE.md`, `.brain/`, and
  `.claude/`
- Codex must not create parallel repo memory, departments, schedules, or hooks
- Codex automations may trigger jobs, but the jobs are defined by the canonical
  repo surfaces and shared engine

This keeps one repo brain and one repo runtime even when both Claude and Codex
operate on the same project.

## Department-Agent Model

Each department is a real repo-local agent contract.

Canonical department files:

- `.claude/departments/<department>.md`
  - mission
  - department goal
  - owned surfaces
  - protected surfaces
  - allowed actions
  - required inputs
  - evaluator and gates
  - stop conditions
  - escalation rules
- `.brain/state/departments/<department>.json`
  - status
  - last run
  - active hypothesis
  - current action
  - confidence score
  - approval state
  - last outcome
- `.brain/knowledge/departments/<department>.md`
  - durable lessons
  - reusable patterns
  - current risks
  - recent failure classes

Every department cycle follows the same loop:

1. Load project, department, skill, approval, and log context.
2. Form one bounded action on owned surfaces only.
3. Run gates before execution.
4. Execute in an isolated lane when code or config changes are required.
5. Judge the outcome against the department evaluator.
6. Learn into department memory, action priors, and project skills when
   promotion rules are met.

Session hooks and cron jobs both dispatch into this same department-cycle
contract.

## Approval State Machine

Strategic approvals are durable repo state.

Canonical files:

- `.brain/state/approval-state.json`
- `.brain/state/pending-approvals.md`

States:

- `inactive`
- `awaiting-project-goal`
- `awaiting-department-goal`
- `awaiting-architecture-change`
- `awaiting-autoresearch-enable`
- `approved`
- `blocked`
- `superseded`

Rules:

- activation cannot enter autonomous execution until project and department
  goals are approved
- department loops must stop when approval state blocks the requested action
- autoresearch cannot start until the repo explicitly approves it
- architecture policy shifts create pending approval records before execution
- both Claude and Codex must read the same approval state before running hooks,
  cron jobs, or automations

This preserves strong operational autonomy without allowing silent strategic
drift.

## Autoresearch Layer

Autoresearch is only available when a repo has an explicit fixed-evaluator
contract.

Canonical files:

- `.brain/autoresearch/program.md`
  - objective
  - mutable surfaces
  - protected surfaces
  - fixed evaluator
  - run command
  - metric extraction rule
  - keep/discard rule
  - runtime budget
  - repair cap
  - max iterations per unattended run
- `.brain/autoresearch/baseline.json`
  - baseline commit
  - baseline metric
  - timestamp
  - evaluator version
- `.brain/autoresearch/results.jsonl`
  - one line per experiment with hypothesis, commit, metric, delta, and status
- `.brain/autoresearch/queue.md`
  - ranked next experiment ideas

Autoresearch process:

1. Load and validate `program.md`.
2. Confirm approvals and protected surfaces.
3. Run and store a baseline before any experiment.
4. Execute one bounded experiment at a time.
5. Keep only genuine improvements with acceptable complexity cost.
6. Revert losing or structurally broken experiments after logging them.
7. Update results, queue, and learned patterns.

Departments without an explicit autoresearch program stay in bounded operational
mode and do not enter keep/discard experiment loops.

## Skill Evolution

Project skills are promoted from validated behavior, not from aspiration.

Canonical files:

- `.brain/knowledge/skills/skill-graph.md`
- `.brain/knowledge/skills/patterns/<skill>.md`

Each promoted skill pattern should capture:

- trigger
- inputs
- constraints
- process
- evaluator
- failure modes
- applied examples

Promotion rules:

- do not promote from a single lucky run
- promote only when a pattern succeeds repeatedly or materially improves
  judgment/execution
- failed experiments update department memory, not the skill graph
- strategic guardrails discovered from failures can become negative-pattern
  skills or operating rules

This makes `.brain` an evolving project capability system rather than a note
dump.

## Global Promotion Inbox

Repo learnings may produce cross-project promotion candidates, but they do not
write directly into global PARA/QMP/skills.

Canonical global review surfaces:

- `~/.claude/knowledge/promotions/inbox.md`
- `~/.claude/knowledge/promotions/<id>.md`

Rules:

- activated repos may emit promotion candidates when a pattern appears reusable
- the global brain reviews candidates during its scheduled architecture and
  memory review loop, and optionally on session start for high-priority items
- approved candidates are promoted into global QMP/resources/skills/decisions
- rejected candidates remain historical evidence and do not affect the global
  operating model

This keeps the global brain stable while still compounding strong learnings.

## Self-Hosting Exception for `compound-brain`

`compound-brain` is not an ordinary client repo.

It is:

- always prepared
- always activated
- always eligible for self-improvement loops

Its hooks and cron jobs should continuously improve:

- the shared `~/.claude` runtime
- the Codex compatibility layer
- preview, prepare, and activation flows
- promotion inbox review
- architecture radar
- runtime observability and logging
- department templates and skill extraction behavior

Routine improvement should not require the user. Only strategic or
contract-breaking changes require approval.

## Architecture Evaluator for `compound-brain`

Self-improvement in `compound-brain` needs a fixed evaluator.

Canonical files:

- `.brain/architecture/evaluator.md`
  - protected invariants
  - architectural rubric
  - deterministic gates
  - keep/discard thresholds
  - review process
- `.brain/architecture/scorecard.json`
  - baseline scores
  - current scores
  - deltas
  - keep/discard decision
  - rationale

The evaluator should be hybrid:

- deterministic checks
  - unit tests
  - installer dry-run
  - activation smoke test
  - self-hosting smoke test
  - no runtime schema drift
- architecture rubric
  - control-plane integrity
  - Claude/Codex parity
  - approval safety
  - repo/global memory separation
  - upgradeability
  - autonomy boundedness
  - observability/log quality
- canary behavior
  - `compound-brain` itself
  - a simple demo repo
  - a more realistic repo

Critical rule:

- self-improvement loops may optimize against the evaluator
- they may not autonomously rewrite the evaluator, rubric, or thresholds
- changes to the evaluator require explicit approval

## Shared Runtime Wiring

Repo-local hooks should remain thin wrappers over a shared engine in
`~/.claude/orchestrator/`.

Shared engine entrypoints:

- `session-start`
- `stop`
- `preview-refresh`
- `prepare-brain`
- `department-cycle`
- `approval-check`
- `autoresearch-cycle`
- `skill-evolution-cycle`
- `promotion-review`

Repo-local wrappers pass the repo path and event name to the shared engine.

Benefits:

- one implementation of gates, approvals, logging, and policy checks
- Claude hooks and Codex automations execute the same logic
- repo-local files stay declarative and inspectable
- activation can refresh wrapper files without overwriting project intelligence

## Scheduling Model

Scheduling has two layers.

Global layer in `~/.claude/`:

- dispatches shared jobs across all seen repos
- refreshes preview cache on first-seen, material change, or cooldown
- runs architecture radar and cross-project synthesis
- reviews the global promotion inbox on schedule
- drives self-hosted `compound-brain` improvement loops

Repo layer in `.claude/settings.local.json` and `.brain/knowledge/crons/crons.md`
for activated repos:

- declares enabled departments
- declares department cadence and runtime budget
- declares whether autoresearch is enabled
- declares which shared events the repo wants scheduled

Prepared-but-not-activated repos do not get repo-local cron or hook jobs.

## Mutation Boundaries

- Global install may improve the overall orchestrator, global memory
  architecture, shared hooks/crons, and architecture radar.
- Preparing or activating one repo must not directly rewrite global PARA/QMP,
  global skills, or global decisions.
- Activated repos write project-specific memory only to their own `.brain/`.
- Cross-project learnings rise upward only through the global promotion inbox
  and scheduled review.

## Upgrade Path

The runtime must support refresh paths for both global and repo surfaces.

- global refresh updates the shared orchestrator and Codex adapter
- `prepare-brain` refresh preserves static project memory
- `activate-repo` refresh updates wrappers and runtime wiring without wiping
  repo intelligence
- `compound-brain` refresh preserves evaluator state, scorecards, and current
  self-hosting logs

This keeps the system upgradeable without losing project or orchestrator
intelligence.
