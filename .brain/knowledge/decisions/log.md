# compound-brain — Decision Log

---

## DEC-001 — Per-project .brain/ knowledge system
**Date:** 2026-03-21
**Priority:** P2
**Context:** Project initialized with isolated .brain/ knowledge system.
**Rule established:** All compound-brain-specific knowledge goes in `.brain/knowledge/`. Global `~/.claude/knowledge/` is for cross-project patterns only.

---

## DEC-002 — Activation-first product architecture
**Date:** 2026-03-21
**Priority:** P1
**Context:** The repo needed a sharper public product boundary than a generic
installer plus background scripts.
**Options Considered:**
- Keep compound-brain as a general framework/template repo
- Build a global-first control plane with thin repo stubs
- Ship a Claude-first activation skill backed by shared and repo-local runtime
  layers
**Reasoning:** The activation-first model gives the community a concrete entry
point: run a skill in a repo and that repo becomes alive. It also preserves
repo-local autonomy while allowing the shared `~/.claude` plane to evolve.
**Expected Outcome:** V1 can be explained, installed, and verified through a
single workflow: activate repo, confirm strategy, materialize local control
surfaces, and start autonomous loops.
**Actual Outcome:** Pending implementation.
**Rule established:** Treat `activate-repo` as the primary product surface.
Global `~/.claude` owns shared orchestration. Activated repos own local
`.brain/`, repo-specific hooks, and department agents.

---

## DEC-003 — Single repo control plane for Claude and Codex
**Date:** 2026-03-21
**Priority:** P1
**Context:** The autonomy layer needed a clear rule for how Claude hooks, Codex
automations, department loops, approvals, and autoresearch share repo state
without drifting into parallel runtimes.
**Options Considered:**
- Keep `.claude/` canonical and let Codex use a separate repo-local overlay
- Let Codex read repo state but restrict it from mutating repo control files
- Treat `.brain/` and `.claude/` as the only repo-level control plane for both
  Claude and Codex
**Reasoning:** A single canonical repo control plane preserves inspectability,
avoids conflicting department definitions or schedules, and lets Codex
automations invoke the same bounded loops as Claude hooks. This also makes
durable approvals and fixed-evaluator autoresearch enforceable across both
tools.
**Expected Outcome:** Activated repos gain one shared runtime contract:
`CLAUDE.md`, `.brain/`, and `.claude/` define behavior; Codex adapters and
automations only dispatch into that same contract.
**Actual Outcome:** Approved for the next implementation pass; design and plan
written.
**Rule established:** Codex must read and honor repo `CLAUDE.md`, `.brain/`,
and `.claude/` before creating skills or automations. Repo-local automations
must execute shared jobs, not invent a second repo runtime.

---

## DEC-004 — Four-state repo lifecycle with self-hosting orchestrator exception
**Date:** 2026-03-21
**Priority:** P1
**Context:** The autonomy model needed a clearer boundary between global
orchestrator installation, static project memory, full repo activation, and the
special case of `compound-brain` itself.
**Options Considered:**
- Activate local autonomy directly on every seen repo
- Keep a two-state model of inactive vs activated
- Use a four-state model for ordinary repos and a self-hosting exception for
  `compound-brain`
**Reasoning:** The four-state model cleanly separates read-only global preview,
static project memory preparation, and explicit local autonomy. It also allows
`compound-brain` to self-improve continuously without forcing every other repo
into the same behavior. The promotion inbox boundary prevents one project from
rewriting global PARA/QMP/skills directly.
**Expected Outcome:** Ordinary repos follow `observe -> preview -> prepare ->
activate`. `compound-brain` remains always prepared and always activated, with
hooks/crons improving the orchestrator against a fixed evaluator.
**Actual Outcome:** Approved and reflected in the revised autonomy design and
implementation plan.
**Rule established:** Global install observes all repos and stores preview state
in `~/.claude`. `prepare-brain` writes only `CLAUDE.md`, `.brain/`, and
`.codex/AGENTS.md`. `activate-repo` creates `.claude/` and turns on local
departments and autonomy. Project learnings rise upward only through the global
promotion inbox.

---

## DEC-005 — Codex global bootstrap and scheduled promotion review
**Date:** 2026-03-21
**Priority:** P2
**Context:** The runtime needed a concrete way for Codex to honor the same
global/repo control plane as Claude, and the new promotion inbox needed an
actual review loop instead of remaining a passive queue.
**Options Considered:**
- Leave Codex compatibility as documentation only
- Add a managed Codex bootstrap plus a scheduled review runner
- Wait for full native Codex hook parity before wiring any runtime support
**Reasoning:** A managed `~/.codex/AGENTS.md` block gives Codex one shared
entrypoint immediately, without creating a second repo runtime. A scheduled
promotion review keeps cross-project learning moving while still requiring
explicit review before global PARA/QMP/skills change.
**Expected Outcome:** Codex starts each repo session from the shared
compound-brain contract, and promotion candidates regularly advance into review
artifacts instead of stagnating in the inbox.
**Actual Outcome:** Implemented on `codex/activate-repo-mvp`; full native Codex
hook parity and automatic canonical promotion remain open work.
**Rule established:** Codex bootstrap is managed through `~/.codex/AGENTS.md`,
and global promotion candidates are reviewed on a scheduled loop before any
cross-project promotion decision.

---

## DEC-006 — Approved global promotions and self-hosting scorecards are runtime jobs
**Date:** 2026-03-21
**Priority:** P2
**Context:** The autonomy branch still had two gaps after initial implementation:
promotion review stopped before canonical global knowledge changed, and the
self-hosting evaluator existed only as files rather than a recurring runtime
check.
**Options Considered:**
- Leave both as manual follow-up work
- Add explicit runtime jobs for approved promotion application and scorecard updates
- Wait for a larger autonomy refactor before wiring either path
**Reasoning:** These two flows are part of the core credibility of
compound-brain. If reviewed candidates cannot land in global QMP/skills/decisions,
or if the self-hosting evaluator never writes a scorecard from real checks, the
system remains architecture-heavy but operationally incomplete.
**Expected Outcome:** Approved promotion candidates can be applied into canonical
global knowledge, and `compound-brain` can periodically score itself against
tests, install dry-runs, rubric checks, and activation smoke runs.
**Actual Outcome:** Implemented on `codex/activate-repo-mvp` together with
evaluator-backed autoresearch execution and repo-cron autoresearch wiring.
**Rule established:** Global promotion review is a two-step runtime path
(`review` then `apply approved`), and self-hosting architecture scorecards must
be produced from real checks rather than remaining static placeholders.

---

## DEC-007 — Activated repos dispatch all local hooks through one shared runtime event engine
**Date:** 2026-03-21
**Priority:** P2
**Context:** Activated repos already had local hook files and shared cron jobs,
but the repo-local hook templates were placeholders rather than real automation
surfaces.
**Options Considered:**
- Leave repo-local hooks as placeholders and rely only on global cron
- Put separate logic into each local hook template
- Dispatch local session-start, stop, and cron hooks into one shared runtime engine
**Reasoning:** A single shared event engine keeps hook behavior aligned across
repos, keeps the system testable, and avoids duplicating autonomy logic into
repo-local template files. It also gives Codex and Claude one clearer contract
for how autoimprovement happens over time.
**Expected Outcome:** Activated repos automatically refresh audits,
intelligence briefs, ranked actions, bounded department cycles, and
autoresearch through local hooks and scheduled cron dispatch.
**Actual Outcome:** Implemented on `codex/activate-repo-mvp` via
`project_runtime_event.py` plus updated repo-local hook templates and global
session/stop wiring.
**Rule established:** Repo-local hooks stay thin wrappers. Shared autoimprovement
behavior lives in one runtime event engine under `~/.claude/scripts/`.

---

## DEC-008 — Scheduled runtime health must be explicit through heartbeats, locks, and watchdog reports
**Date:** 2026-03-22
**Priority:** P2
**Context:** After hook-driven autoimprovement was added, the remaining trust gap
was operational: scheduled loops could run, but there was no durable proof of
coverage, overlap prevention, or missed-heartbeat visibility.
**Options Considered:**
- Trust cron and hook execution implicitly
- Add lightweight logging only
- Add explicit heartbeats, lockfiles, failure backoff, and watchdog reporting
**Reasoning:** If autonomous loops are meant to be relied on, they need the same
operational surfaces that make background systems trustworthy: last success,
next due time, overlap protection, and a visible report when coverage degrades.
**Expected Outcome:** Activated repos expose durable heartbeat state, overlapping
runs are blocked, failures back off predictably, and the global brain can show
which repos are healthy, overdue, or missing runtime coverage.
**Actual Outcome:** Implemented on `codex/activate-repo-mvp` via
`runtime_heartbeat.py`, `runtime_watchdog.py`, and runtime-event integration.
**Rule established:** Hook/cron autonomy is not considered trustworthy unless it
produces explicit heartbeat state and watchdog-visible coverage.

---

## DEC-009 — Activated repos track capability-driven skill state and materialize best-fit repo skills
**Date:** 2026-03-21
**Priority:** P2
**Context:** The activation/runtime branch could already promote skills after
successful work, but it still lacked a repo-aware loop that audited what a repo
actually needed, matched that against local/global skills, and kept explicit
state for which skills were active, stale, missing, or worth materializing.
**Options Considered:**
- Leave skill growth reactive only, driven by later department outcomes
- Add repo-aware capability inference plus local/global/external skill matching
- Depend only on manual skill authoring per repo
**Reasoning:** If the orchestrator is meant to make repos more capable over
time, it needs an explicit map of what the repo is missing now. Matching
repo-local skills first keeps the system grounded in project-specific knowledge,
matching global skills second enables cross-project reuse, and conservative
external matching lets approved skills help without creating noisy drift.
**Expected Outcome:** Activated repos write `.brain/state/skills.json`, keep
active/stale/missing skill state current during activation and runtime events,
and materialize the highest-fit repo skills into `.brain/knowledge/skills/`
when confidence is high enough.
**Actual Outcome:** Implemented on `codex/activate-repo-mvp` through
`skill_inventory.py`, activation/runtime wiring, tests, and updated docs.
**Rule established:** Repo skill matching must be capability-driven and
source-ordered: repo-local first, global second, approved external last.

---

## DEC-010 — Activated repos must carry explicit autonomy depth, trust, and preload state
**Date:** 2026-03-21
**Priority:** P2
**Context:** The activation/runtime branch already had hooks, cron, skills, and
bounded autonomy, but it still treated activated repos too uniformly and still
depended too much on the model remembering to read the right files before
acting.
**Options Considered:**
- Keep one fixed autonomy level for all activated repos
- Add a user-capped, repo-local depth governor with required-context preload and trust scoring
- Leave depth and preload behavior implicit inside prompts only
**Reasoning:** To make the repo brain feel like the model's operating soul,
autonomy must be explicit, adaptive, and fail-closed. That requires a global
user ceiling, per-repo current depth, deterministic required-context rules,
compact runtime packets, and trust signals from heartbeat, skills, approvals,
and validation instead of letting Claude/Codex improvise their own depth.
**Expected Outcome:** Activated repos write explicit depth/governor/packet/context
files, cron stays planning-only at low depth, deeper execution is unlocked only
by evidence, and both Claude and Codex wake into the same compact runtime
reality every session.
**Actual Outcome:** Implemented on `codex/activate-repo-mvp` through global
policy seeds, repo depth/governor state, fail-closed context snapshots,
runtime packets, department source-pack scaffolding, and depth-aware cron
behavior.
**Rule established:** Repo autonomy must be policy-driven and preload-verified:
global user cap first, repo depth second, context snapshot before action.

---

## DEC-011 — Cross-department agreement and trust history are required for depth evolution
**Date:** 2026-03-22
**Priority:** P2
**Context:** After the initial autonomy-depth governor landed, activated repos
could vary depth and preload context correctly, but they still lacked two
critical safeguards: department objections were not first-class runtime gates,
and depth changes leaned too heavily on single-cycle trust scores.
**Options Considered:**
- Keep depth movement based mostly on the current trust score
- Add cross-department arbitration but keep it advisory only
- Add explicit department agreement state plus trust history and healthy streaks
  as inputs to depth raise/lower behavior
**Reasoning:** If the runtime is meant to act like an experienced orchestrator,
it needs both horizontal judgment and temporal judgment. Horizontal judgment
comes from departments being able to object when a risky action crosses their
lane. Temporal judgment comes from trend and healthy-streak evidence rather
than one good or bad cycle. Together they make autonomous depth more credible
and less likely to overreach.
**Expected Outcome:** Activated repos write department-agreement state on each
event, cron drops back to planning-only when operations or architecture object,
and depth raises/lowering reflect trust history and recent healthy streaks.
**Actual Outcome:** Implemented on `codex/activate-repo-mvp` with new runtime
tests and verified by the full unittest suite plus installer dry-run.
**Rule established:** Repo autonomy depth must evolve from trust history and
department agreement, not from point-in-time score alone.

---

## DEC-012 — Community contributions should land in bounded lanes before touching the runtime core
**Date:** 2026-03-22
**Priority:** P2
**Context:** After the main activation/runtime system became coherent, the next
growth challenge was how to let the community improve the project without
turning the orchestration kernel into an unreviewable stream of ad hoc ideas.
**Options Considered:**
- Accept most community changes directly into the core runtime
- Keep community input mostly in discussions and ad hoc issues
- Add explicit contribution lanes for skills, departments, source packs,
  evaluators, case studies, benchmarks, and promotion candidates
**Reasoning:** The system needs outside learning, but it also needs a stable
control plane. Bounded contribution lanes let the community provide evidence,
patterns, and reusable building blocks while maintainers preserve the kernel’s
approval, depth, and runtime guarantees.
**Expected Outcome:** Contributors have clear places to submit high-value work,
maintainers have a promotion workflow, and the runtime improves through
evidence-backed artifacts rather than noisy direct mutation.
**Actual Outcome:** Implemented through `community/`, GitHub issue forms, a PR
template, and maintainer review docs.
**Rule established:** Default community growth goes through bounded lanes first;
core runtime changes require stronger evidence and review.

---

## DEC-013 — `compound-brain` may auto-route eligible self-hosting cron work into Ralph
**Date:** 2026-03-22
**Priority:** P2
**Context:** The self-hosting repo already had bounded cron execution, but some
multi-step implementation lanes benefit from a fresh-context outer loop instead
of repeatedly pushing deeper work through the normal cron executor.
**Options Considered:**
- Keep all self-hosting cron work on the normal bounded runtime
- Make Ralph always-on for every `compound-brain` runtime event
- Auto-route only eligible self-hosting cron work into a one-story Ralph loop
**Reasoning:** Ralph is valuable when the work is multi-step and still
deterministically gated, but making it universal would overload lightweight
maintenance cycles. A narrow gate preserves cheap default cron behavior while
still letting `compound-brain` use Ralph automatically for healthy,
approved feature/debt/research lanes.
**Expected Outcome:** Eligible `compound-brain` cron runs generate or refresh a
single PRD, execute one Ralph iteration, and record durable Ralph state without
changing the behavior of ordinary repos or low-trust self-hosting cycles.
**Actual Outcome:** Implemented through `ralph-policy.json`,
`scripts/lib/ralph_mode.py`, runtime packet mode selection, auto-generated PRD
materialization, and cron-side Ralph dispatch.
**Rule established:** Only `compound-brain` may auto-route into Ralph, only on
eligible cron lanes, and only when depth, trust, healthy streak, approvals, and
department agreement all pass the Ralph policy gate.

---

## DEC-014 — `compound-brain` should optimize for proactive operator behavior, not passive question answering
**Date:** 2026-03-23
**Priority:** P1
**Context:** The architecture had already accumulated hooks, cron heartbeats,
department lanes, approvals, skills, QMP, logs, and trust/depth governance, but
the repo still needed a sharper statement of what all of that is for.
**Options Considered:**
- Keep the system framed primarily as a shared orchestration layer
- Let proactivity remain an implied property of the runtime
- State explicitly that `compound-brain` exists to turn LLMs into proactive,
  memory-driven project operators
**Reasoning:** The system is strongest when it does more than answer the last
prompt. Hooks and cron heartbeats should wake the runtime, preload project
memory, select the right department lane, recommend the next best bounded move,
and act when evidence and approvals allow it. Making that principle explicit
aligns the docs, project brain, and runtime contract around one credible goal.
**Expected Outcome:** Public docs, repo strategy, and future implementation work
all optimize for proactive recommendation and bounded execution from memory,
while still avoiding hype about perfect certainty or unlimited autonomy.
**Actual Outcome:** README, architecture docs, and the project record now carry
this rule explicitly.
**Rule established:** `compound-brain` should behave like a proactive,
memory-driven project operator. It should recommend and execute the next best
bounded moves from evidence, while strategic direction remains approval-gated
and confidence remains evidence-weighted rather than absolute.

---

## DEC-015 — Activated repos should persist an explicit operator brief on every runtime wake-up
**Date:** 2026-03-23
**Priority:** P2
**Context:** The runtime already computed ranked actions, lead departments,
approvals, skills, and trust, but that state was scattered across multiple
files. The proactive operator model needed one canonical answer to: what should
happen next, which department is active, what is blocked, and why.
**Options Considered:**
- Keep the runtime state distributed across packet, governor, queue, and skills
  files
- Depend on the LLM to reconstruct the current operator stance from raw state
- Persist an explicit operator recommendation and latest operator brief on every
  session-start, cron, and stop event
**Reasoning:** A proactive system should not make the model or the user rebuild
the current next move from scratch every session. Writing one operator brief
turns the existing state into a compact control surface that both humans and
LLMs can trust quickly.
**Expected Outcome:** Activated repos always carry a current recommendation file
and latest brief showing the lead department, supporting departments, blocked
approvals, trust score, missing skills, and next bounded action.
**Actual Outcome:** Implemented in the shared runtime governor and event engine,
covered by runtime-governor and project-runtime tests.
**Rule established:** Every activated runtime wake-up should persist a compact
operator recommendation, not just low-level state files.

---

## DEC-004 — Add pre-tool-use write guard for protected surfaces
**Date:** 2026-03-22
**Priority:** P1
**Context:** Department contracts define protected surfaces (e.g. lib/storage/, .env.local,
evaluator contracts) but nothing technically prevents either Claude Code or Codex from
writing to them. Rules are instruction-based, not enforced. An LLM can skip them.
**Options Considered:**
- Option A: Pre-tool-use hook that checks write path against department protected surfaces
- Option B: Filesystem permissions (chmod) on protected paths
- Option C: Leave as instruction-only (current state)
**Reasoning:** Option A is the right layer — hooks fire before every tool use, can read
department contracts, and can block writes to protected paths without breaking normal flow.
Option B is fragile (permissions get reset). Option C is the current gap.
**Expected Outcome:** Any write attempt to a protected surface is blocked by the hook,
logged to .brain/knowledge/areas/skill-health.md, and surfaced to the human.
**Rule established:** Implement `pre_tool_use_write_guard.py` hook that reads
`.claude/departments/*.md` Protected Surfaces sections and blocks writes to listed paths.
Both Claude Code and Codex must be wired to this hook.

---

## DEC-016 — Activated repos should execute through mission packets, department shopping, and isolated autoresearch lanes
**Date:** 2026-03-23
**Priority:** P1
**Context:** The runtime already had approvals, depth, arbitration, and
bounded department cycles, but the remaining gaps were clear: department
execution still behaved like a queue pop instead of a multi-department lane,
skill matching still lacked strong department adaptation, and autoresearch did
not yet isolate mutations from the main working tree.
**Options Considered:**
- Keep the existing bounded queue/runtime and rely on future refinements
- Add a second orchestration layer just for deeper execution
- Deepen the existing runtime with mission packets, department-aware skill
  shopping, and worktree-isolated mutation lanes
**Reasoning:** A second orchestrator would create control-plane drift. The
stronger approach is to deepen the current shared runtime so Claude and Codex
still wake into one repo brain, but each department now gets a concrete mission
packet, supporting departments can enter queued handoff lanes, skill shopping
stores match reasons/trust/freshness/adaptation in department state, and
autoresearch can mutate and evaluate in a temporary worktree before copying
only winning changes back.
**Expected Outcome:** Activated repos feel more like a real multi-department
operator: lead departments write staged missions, supporting departments are
explicitly queued, skill adoption is repo-adapted instead of title-matched, and
evaluator-backed experiments no longer dirty the main checkout during discard
cycles.
**Actual Outcome:** Implemented in `department_cycle.py`,
`skill_inventory.py`, `run_project_llm_cron.py`, `project_runtime_event.py`,
and `autoresearch_runner.py`, with regression coverage in dedicated tests.
**Rule established:** Deeper autonomy should extend the existing shared
runtime, not bypass it. Department execution must be mission-based, skill
adoption must be department-aware, and mutation experiments must run in
isolated lanes.

---

## DEC-017 — Codex should enter the same runtime through a managed bridge, and external skill intelligence should be cached globally
**Date:** 2026-03-23
**Priority:** P1
**Context:** After mission packets, deeper skill shopping, and isolated
autoresearch landed, two gaps remained in the vision: Codex still relied on a
bootstrap document more than a real runtime wake protocol, and repo skill
shopping still depended too heavily on repo-local/global skills plus approved
skill roots instead of a broader external intelligence loop.
**Options Considered:**
- Keep Codex parity at documentation/bootstrap level and leave external skill discovery mostly local
- Add a separate Codex-only runtime or scheduler plus repo-local GitHub scans
- Add a managed Codex runtime bridge into the shared event engine and a global
  cached skill radar fed by GitHub plus activated-repo tips
**Reasoning:** The third option preserves one control plane. Codex can wake
through the same runtime by reusing fresh repo state or dispatching the same
`session-start` event Claude uses, while the global plane can absorb broader
GitHub intelligence on a fixed cron and feed ranked candidates back into repo
skill shopping without forcing every session to hit GitHub directly. That
keeps parity credible, sessions fast, and skill acquisition more intelligent.
**Expected Outcome:** Codex starts activated repos from the same operator brief
and runtime packet as Claude, global cron writes `skill-catalog.json` and
`project-tip-catalog.json`, and repo skill refresh can materialize or propose
better-fit skills from cached external evidence plus local project tips.
**Actual Outcome:** Implemented through `codex_runtime_bridge.py`,
`skill_radar_refresh.py`, `scripts/lib/skill_radar.py`, updated installer and
bootstrap wiring, and skill-inventory/runtime-governor integration, with new
regression tests covering the bridge, radar, install path, and operator
opportunity surfacing.
**Rule established:** Codex parity should happen through one managed bridge
into the shared runtime, and broader external skill intelligence should be
gathered globally on cron, cached in `~/.claude`, and consumed by repo-local
skill shopping rather than by ad hoc per-session web searching.
