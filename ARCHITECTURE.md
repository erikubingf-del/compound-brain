# compound-brain — Architecture

## Operating principle

`compound-brain` is designed to make LLMs behave like proactive, memory-driven
project operators, not passive question-answer systems.

That means:

- hooks and cron jobs wake one shared runtime
- the runtime preloads bounded context before reasoning
- departments decide who should lead the current lane
- the system recommends the next best bounded move from evidence
- approvals, trust, and evaluators keep that proactivity credible

The target is evidence-weighted high confidence, not claims of perfect
certainty.

## Lifecycle

Ordinary repos follow:

1. `observe`
2. `preview`
3. `prepare`
4. `activate`

Only the global plane operates before activation.

## Global plane

Lives in `~/.claude/`.

Responsibilities:
- shared hooks and cron dispatch
- global PARA/QMP/skills/decisions
- global autonomy-depth and required-context policy
- repo preview cache
- activation registry
- promotion inbox
- architecture radar
- skill radar and project-tip catalog
- shared runtime for Claude and Codex triggers

Mutation rule:
- global knowledge changes only through explicit global logic and promotion review
- one activated repo cannot directly rewrite the shared operating model

## Repo plane

Prepared repo:
- `CLAUDE.md`
- `.brain/`
- `.codex/AGENTS.md`

Activated repo adds:
- `.claude/settings.local.json`
- `.claude/hooks/`
- `.claude/departments/`
- approval state
- autonomy-depth state
- runtime governor state
- runtime packet
- context snapshot
- department state
- skill state
- autoresearch state

## Shared control plane

Activated repos use one canonical local control plane:

- `CLAUDE.md`
- `.brain/`
- `.claude/`

Codex reads the same surfaces through `.codex/AGENTS.md`. It must not create a
parallel repo runtime. The managed bootstrap now routes activated repos through
`~/.claude/scripts/codex_runtime_bridge.py`, which reuses fresh runtime state
when possible and falls back to the same `session-start` event engine Claude
uses. Recurring Codex parity is handled by managed automation definitions under
`~/.codex/automations/`, which wake the same shared runtime on schedule instead
of creating a second scheduler model.

## Department runtime

Each department has:
- contract: `.claude/departments/<department>.md`
- state: `.brain/state/departments/<department>.json`
- memory: `.brain/knowledge/departments/<department>.md`
- mission packet: `.brain/state/departments/<department>-mission.json`

Cycle shape:
- load context
- check approval
- build one mission packet
- stage analyze -> execute -> verify
- hand off to the right supporting department when needed
- log result and follow-up actions
- stop or escalate

Operator expectation:
- `session-start` should surface what matters next
- `user-request` should merge user intent with repo memory and department scope
- `cron` should keep the repo moving between sessions when evidence says it is
  safe
- `stop` should convert work into durable experience

Runtime governance:
- every event writes `.brain/state/context-snapshot.json`
- every event writes `.brain/state/runtime-packet.json`
- every event refreshes `.brain/state/runtime-governor.json`
- every event refreshes `.brain/state/department-agreement.json`
- repo depth lives in `.brain/state/autonomy-depth.json`
- department source packs live in `.brain/knowledge/departments/<department>-sources.md`
- department skill-shopping state lives in `.brain/state/departments/<department>-shopping.json`

Hook and cron wiring:
- `project_session_start.py` dispatches to the shared runtime event engine
- `project_stop.py` dispatches to the shared runtime event engine
- `project_llm_cron.py` dispatches to the shared runtime event engine
- the shared engine refreshes audits, intelligence briefs, ranked actions, and bounded runtime cycles
- cron can now carry a lead mission into verifier handoff state instead of treating every pass as a flat queue pop

Heartbeat expectation:
- hooks wake the runtime on session boundaries
- cron provides recurring heartbeats between sessions
- heartbeats should identify the active department lane, blocked approvals,
  recommended next action, and whether the repo can safely execute or should
  stay in planning mode

Depth behavior:
- depth `2` keeps cron in planning-only mode
- depth `3` allows bounded department execution
- depth `4+` allows evaluator-backed autoresearch
- department objections can force cron back into planning-only mode even at higher depths
- depth lowers automatically when approvals, trust, or context compliance fail

Operational trust layer:
- heartbeat records live in `~/.claude/registry/runtime-heartbeats/`
- lockfiles live in `~/.claude/registry/runtime-locks/`
- cron failures enter backoff instead of silently flapping
- watchdog reports missed or missing heartbeats to `~/.claude/knowledge/resources/runtime-heartbeats.md`
- runtime-governor history tracks trust trend and healthy streaks for depth evolution

Cross-department arbitration:
- one lead department owns the action lane
- supporting departments can agree, agree with constraints, or object
- operations objections gate infra/runtime work
- architecture objections gate control-plane and high-risk structural work

## Approval model

Strategic approvals live in:
- `.brain/state/approval-state.json`
- `.brain/state/pending-approvals.md`

These gate:
- project goal
- department goals
- architecture changes
- autoresearch enablement

Before confirmation, activation may also store a recommendation packet in the
approval state so the user sees a stronger proposed `project_goal` or
repo-native department alignment before approving strategy.

This preserves the right split:
- the runtime should proactively recommend what should happen next
- the user still owns strategic direction changes

## Autoresearch model

Autoresearch only runs with:
- explicit program contract
- fixed evaluator
- approval

Files:
- `.brain/autoresearch/program.md`
- `.brain/autoresearch/baseline.json`
- `.brain/autoresearch/results.jsonl`
- `.brain/autoresearch/queue.md`

If `program.md` includes a `Mutation Command`, the runtime creates a temporary
worktree lane, runs the mutation there, enforces `Mutable Surfaces`, evaluates
the candidate there, and only copies changes back into the repo when the
keep/discard rule says to keep them.

## Learning model

Project-local skill promotion:
- `.brain/knowledge/skills/skill-graph.md`
- `.brain/knowledge/skills/patterns/*.md`
- `.brain/state/skills.json`

Repo skill discovery flow:
- infer required capabilities from repo stack, docs, tests, departments, and autoresearch state
- match repo-local skills first
- match global shared skills second
- match global skill-radar candidates and project-tip evidence next
- match approved external skill roots last
- score candidates with department source-pack context, trust, freshness, and adaptation notes
- materialize best-fit skills into the repo brain when the match is strong enough
- keep explicit active, stale, recommended, and missing skill state per repo

Global skill-intelligence flow:
- `skill_radar_refresh.py` runs on cron in the global plane
- it searches approved GitHub patterns with star thresholds and department-aware queries
- it extracts reusable project tips from activated repos
- it writes `skill-catalog.json`, `project-tip-catalog.json`, and `skill-radar-latest.md`
- repo runtime wakes consume those cached catalogs during normal skill refresh

Cross-project candidates:
- `~/.claude/knowledge/promotions/inbox.md`
- `~/.claude/knowledge/promotions/*.json`
- `~/.claude/scripts/review_promotion_inbox.py`
- `~/.claude/scripts/apply_approved_promotions.py`

Promotion flow:
- repo submits candidate
- global review loop generates review artifact
- approved candidates are applied to canonical global knowledge

## Self-hosting exception

`compound-brain` itself is always prepared and always activated.

It self-improves against:
- `.brain/architecture/evaluator.md`
- `.brain/architecture/scorecard.json`
- `scripts/update_architecture_scorecard.py`
- `scripts/nightly_review.sh`
- `~/.claude/policy/ralph-policy.json`

For self-hosting implementation lanes, `compound-brain` may also auto-route
eligible cron work into Ralph:
- repo must be `compound-brain`
- event must be `cron`
- depth must meet the Ralph minimum
- trust and healthy streak must meet policy thresholds
- no pending strategic approvals
- no architecture or operations veto
- top action category must be eligible

If those gates pass, the runtime materializes a single-story PRD in
`.agents/tasks/prd-compound-brain-auto.json`, runs one Ralph iteration, and
records the outcome in `.brain/state/ralph-state.json`.

The evaluator is approval-gated and cannot be silently rewritten by the runtime.
