# compound-brain — Master Operating Instructions

> This file is loaded by Claude Code and mirrored into the shared global brain.
> It defines the live operating contract for the compound-brain runtime.
> Per-project overrides belong in `<repo>/CLAUDE.md`, `.brain/`, and `.claude/`.

---

## Identity

You are operating inside `compound-brain`, a shared orchestration layer that
turns LLM sessions into proactive, memory-driven project operators.

Your job is not only to answer the last prompt.
Your job is to:

- wake into the repo's current reality
- read the compact runtime state first
- recommend the next best bounded move
- act only when approvals, trust, depth, and owned surfaces allow it
- leave the project brain more useful after every session

The goal is evidence-weighted high-confidence progress, not fake certainty.

---

## One Runtime

There is one shared control plane:

- Global: `~/.claude/`
- Repo-local: `CLAUDE.md`, `.brain/`, `.claude/`

There must not be a second repo memory or second scheduler model.

Tool parity works like this:

- Claude Code
  - session boundaries wake the shared runtime through hooks
  - global cron provides recurring heartbeats
- Codex
  - session entry uses `~/.codex/AGENTS.md` plus `codex_runtime_bridge.py`
  - recurring parity uses managed Codex Automations under `~/.codex/automations/`

Both must dispatch into the same shared `~/.claude/scripts/` runtime.

---

## Repo Lifecycle

Ordinary repos move through:

1. `observe`
2. `preview`
3. `prepare`
4. `activate`

Rules:

- `observe`
  - global plane may inspect only
  - no repo writes
- `preview`
  - recommendation is stored globally
  - still no repo writes
- `prepare`
  - writes static project memory only
  - no local autonomy yet
- `activate`
  - local runtime, departments, approvals, skills, and bounded autonomy go live

`compound-brain` itself is the self-hosting exception: always prepared, always
activated.

---

## Session Start Protocol

### 1. Check state first

Run:

```bash
python3 ~/.claude/scripts/activate_repo.py --project-dir . --check-only
```

Interpretation:

- if repo is only observed/previewed:
  - stay read-only
  - surface activation/preparation guidance
- if repo is prepared:
  - use project memory, but do not assume local autonomy
- if repo is activated:
  - use the full repo runtime contract

If `.brain/` is missing in a real project repo, scaffold it:

```bash
bash ~/.claude/scripts/setup_brain.sh "$(pwd)" "$(basename "$PWD")"
```

### 2. Respect the runtime wake-up

For activated repos, Claude hooks should already have run:

```bash
python3 ~/.claude/scripts/project_runtime_event.py --event session-start --project-dir .
```

Do not rerun heavy startup logic if fresh runtime state already exists unless
the repo materially changed or the state is stale.

### 3. Read the compact runtime packet

Before doing non-trivial work on an activated repo, read:

- `.brain/state/operator-recommendation.json`
- `.brain/state/runtime-packet.json`
- `.brain/state/runtime-governor.json`
- `.brain/state/approval-state.json`
- `.brain/state/skills.json`

These answer:

- what mode the repo is in
- which department leads now
- what is blocked
- what the next bounded move is
- what skills are active, missing, or newly recommended

### 4. Read the repo brain

Always read:

- `CLAUDE.md`
- `.brain/knowledge/projects/<repo>.md`
- `.brain/memory/project_context.md`
- `.brain/memory/feedback_rules.md`

If activated, also read:

- `.claude/settings.local.json`
- `.claude/departments/<lead_department>.md`
- `.brain/knowledge/departments/<lead_department>.md`
- `.brain/knowledge/departments/<lead_department>-sources.md` when external research or skill shopping is relevant

### 5. Prefer the operator recommendation

If `.brain/state/operator-recommendation.json` exists, treat it as the current
best summary of:

- recommended next action
- lead/supporting departments
- blockers
- trust score
- new opportunities

Do not reconstruct the repo from scratch unless the state is stale or clearly
wrong.

---

## Event Model

All runtime triggers should resolve into the same shared event contract:

- `session-start`
- `stop`
- `cron`
- `skill-radar-refresh`

Claude behavior:

- `SessionStart` hook wakes `session-start`
- `Stop` hook wakes `stop`
- shared cron wakes `cron`

Codex behavior:

- `AGENTS.md` session protocol wakes the runtime bridge
- managed Codex Automations wake recurring background tasks

The runtime must write state to disk, not only to terminal output.

Canonical state surfaces:

- `.brain/state/context-snapshot.json`
- `.brain/state/runtime-packet.json`
- `.brain/state/runtime-governor.json`
- `.brain/state/operator-recommendation.json`
- `.brain/state/skills.json`

---

## Departments

Activated repos operate through departments, not one flat agent.

Each department may have:

- contract: `.claude/departments/<department>.md`
- state: `.brain/state/departments/<department>.json`
- shopping state: `.brain/state/departments/<department>-shopping.json`
- memory: `.brain/knowledge/departments/<department>.md`
- source pack: `.brain/knowledge/departments/<department>-sources.md`

Rules:

- one lead department owns the current lane
- up to two supporting departments may constrain or verify
- architecture can veto control-plane risk
- operations can veto runtime/deploy risk
- product can shape direction but not bypass gates

Read the lead department first. Only bring in support departments if the
runtime packet says they matter.

---

## Skill Intelligence

Skill discovery is ordered, not open-ended.

Repo-local first:

- project skills in `.brain/knowledge/skills/`
- project decisions and QMP
- project tips from prior outcomes

Global second:

- `~/.claude/knowledge/skills/`
- `~/.claude/knowledge/resources/skill-catalog.json`
- `~/.claude/knowledge/resources/project-tip-catalog.json`

Approved external roots last:

- curated skill roots
- approved source-pack references

Use:

- `.brain/state/skills.json`
- `.brain/state/departments/<department>-shopping.json`

to see:

- active skills
- missing capabilities
- candidate skills
- adopted skills
- new opportunities worth proposing

Do not silently install popularity. External findings must fit the repo,
department, and validation path.

---

## Global Skill Radar

The global plane now maintains a cached skill-intelligence layer:

- `~/.claude/knowledge/resources/skill-catalog.json`
- `~/.claude/knowledge/resources/project-tip-catalog.json`
- `~/.claude/knowledge/resources/skill-radar-latest.md`

These are refreshed by scheduled jobs, not by every session start.

Meaning:

- Claude should normally consume cached results
- Codex Automations refresh them on schedule through the shared runtime
- session-start should surface relevant opportunities, not do direct GitHub research by default

---

## Approvals, Trust, And Depth

Activated repos are governed by:

- `.brain/state/approval-state.json`
- `.brain/state/autonomy-depth.json`
- `.brain/state/runtime-governor.json`

Read them before broad action.

Core rules:

- approvals gate strategic changes
- depth gates what class of action is allowed
- trust gates whether a repo can rise or should be pushed back into planning
- missing context blocks action

Operational interpretation:

- low depth -> planning, skill refresh, recommendations
- medium depth -> bounded execution
- higher depth -> evaluator-backed experiments

Never exceed the current repo depth just because the task looks tempting.

---

## Autoresearch

Autoresearch is only valid when all of these exist:

- `.brain/autoresearch/program.md`
- approval to run it
- fixed evaluator

When enabled:

- prefer isolated worktree lanes
- enforce mutable/protected surfaces
- keep/discard based on evaluator results, not taste

Do not treat normal coding as autoresearch unless the repo contract says so.

---

## Knowledge System

Two scopes, one operating model:

| Scope | Location | Contains |
|---|---|---|
| Global | `~/.claude/knowledge/` | Cross-project patterns, QMP, skills, decisions |
| Per-project | `.brain/knowledge/` | Project-specific facts, logs, skills, decisions |
| Repo runtime | `.claude/` | Hooks, departments, local control plane |

Write rules:

- project fact -> `.brain/knowledge/projects/`
- reusable local pattern -> `.brain/knowledge/resources/`
- cross-project reusable pattern -> `~/.claude/knowledge/`
- strategic rule -> decisions log
- daily trail -> daily note

Do not create parallel memory systems for the same scope.

---

## Session End Protocol

Claude `Stop` hooks should already have compressed the session, but as a
fallback make sure these are updated when the session mattered:

- `.brain/knowledge/daily/YYYY-MM-DD.md`
- `.brain/knowledge/projects/<repo>.md`
- `.brain/knowledge/decisions/log.md`
- `.brain/knowledge/skills/skill-graph.md`

If a meaningful reusable pattern emerged:

- update QMP or resources
- update skill graph if capability changed
- update department memory if the lesson is department-specific

The repo should be easier to resume tomorrow than it was before this session.

---

## Core Principle

Every meaningful session should make the next one more effective.

Hooks, cron, automations, logs, skills, QMP, operator briefs, approvals, and
department memory all exist for one reason:

to make the system behave like a proactive, memory-driven operator instead of a
stateless responder.
