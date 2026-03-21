# Activate Repo Autonomy Layer Design

**Date:** 2026-03-21
**Status:** Approved

## Goal

Extend the `activate-repo` MVP so an activated repo can run real department
agent loops, durable strategic approvals, fixed-evaluator autoresearch, and
project-specific skill evolution while keeping Claude and Codex on the same
repo control plane.

## Product Decisions

- `.brain/` and `.claude/` are the only canonical repo-level control surfaces.
- `CLAUDE.md` remains the human-readable project operating contract.
- Claude hooks and Codex automations must invoke the same repo jobs and write to
  the same repo state.
- Department loops are bounded, evaluator-aware, and scoped to owned surfaces.
- Strategic confirmations are durable state, not transient chat-only approvals.
- True autoresearch requires an explicit program contract and a fixed evaluator.
- Project-specific skills only promote from validated repeatable patterns.

## Shared Control Plane

Every alive repo has one local operating surface:

- `CLAUDE.md` for project instructions and operating rules
- `.brain/` for memory, approvals, decisions, goals, skills, QMP, logs, and
  autoresearch state
- `.claude/` for executable control-plane assets such as hook wrappers, local
  settings, and department specs

Codex compatibility is implemented as a thin adapter, not as a second brain:

- activation may generate `.codex/AGENTS.md`
- the adapter instructs Codex to read `CLAUDE.md`, `.brain/`, and `.claude/`
- the adapter forbids parallel repo memory, departments, or schedules
- Codex automations must invoke the same repo-local or shared jobs that Claude
  uses

This keeps one canonical repo runtime even when multiple operator clients are
attached to the same project.

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
5. Judge the outcome against the action evaluator.
6. Learn into department memory, action priors, and project skills when
   promotion rules are met.

Session and cron hooks both dispatch into this same department-cycle contract.

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

## Shared Runtime Wiring

Repo-local hooks should remain thin wrappers over a shared engine in
`~/.claude/orchestrator/`.

Shared engine entrypoints:

- `session-start`
- `stop`
- `department-cycle`
- `approval-check`
- `autoresearch-cycle`
- `skill-evolution-cycle`

Repo-local wrappers pass the repo path and event name to the shared engine.

Benefits:

- one implementation of gates, approvals, logging, and policy checks
- Claude hooks and Codex automations execute the same logic
- repo-local files stay declarative and inspectable
- activation can refresh wrapper files without overwriting project intelligence

## Scheduling Model

Scheduling has two layers.

Global layer in `~/.claude/`:

- dispatches shared jobs across activated repos
- runs architecture radar and cross-project synthesis
- can invoke repo cycles into alive repos

Repo layer in `.claude/settings.local.json` and `.brain/knowledge/crons/crons.md`:

- declares enabled departments
- declares department cadence and runtime budget
- declares whether autoresearch is enabled
- declares which shared events the repo wants scheduled

Codex automations may mirror these jobs, but they do not define novel behavior.

## Run Safety

Every runtime entrypoint must preflight:

- approval state
- owned and protected surfaces
- evaluator availability when required
- run budget and repair cap
- current department status
- correct log targets

If preflight fails, the loop records the reason and stops cleanly instead of
drifting into uncontrolled execution.

## Upgrade Path

Activation must also support a repo refresh flow:

- re-read current `.brain/`, `.claude/`, and `.codex/AGENTS.md`
- update wrapper scripts and adapters to the current runtime version
- preserve local department definitions, approvals, and learned skills
- preserve repo-specific autoresearch programs and results

This keeps the shared runtime upgradeable without wiping local intelligence.
