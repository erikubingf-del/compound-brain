# compound-brain — Architecture

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
- repo preview cache
- activation registry
- promotion inbox
- architecture radar
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
- department state
- autoresearch state

## Shared control plane

Activated repos use one canonical local control plane:

- `CLAUDE.md`
- `.brain/`
- `.claude/`

Codex reads the same surfaces through `.codex/AGENTS.md`. It must not create a
parallel repo runtime.

## Department runtime

Each department has:
- contract: `.claude/departments/<department>.md`
- state: `.brain/state/departments/<department>.json`
- memory: `.brain/knowledge/departments/<department>.md`

Cycle shape:
- load context
- check approval
- choose one bounded action
- log result
- stop or escalate

Hook and cron wiring:
- `project_session_start.py` dispatches to the shared runtime event engine
- `project_stop.py` dispatches to the shared runtime event engine
- `project_llm_cron.py` dispatches to the shared runtime event engine
- the shared engine refreshes audits, intelligence briefs, ranked actions, and bounded runtime cycles

Operational trust layer:
- heartbeat records live in `~/.claude/registry/runtime-heartbeats/`
- lockfiles live in `~/.claude/registry/runtime-locks/`
- cron failures enter backoff instead of silently flapping
- watchdog reports missed or missing heartbeats to `~/.claude/knowledge/resources/runtime-heartbeats.md`

## Approval model

Strategic approvals live in:
- `.brain/state/approval-state.json`
- `.brain/state/pending-approvals.md`

These gate:
- project goal
- department goals
- architecture changes
- autoresearch enablement

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

## Learning model

Project-local skill promotion:
- `.brain/knowledge/skills/skill-graph.md`
- `.brain/knowledge/skills/patterns/*.md`

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

The evaluator is approval-gated and cannot be silently rewritten by the runtime.
