---
title: compound-brain
status: active
updated: 2026-03-22
---

# compound-brain

## Goal
Build a public GitHub framework and activation skill that makes an opted-in repo
"alive" by installing a global orchestrator once, previewing repos read-only by
default, preparing static project brains on request, and activating repo-local
departments and bounded autonomous loops only when explicitly enabled.

## Status
Architecture direction approved. The repo already has a first-pass installer,
brain scaffold, auditor, intelligence scripts, and docs. The next milestone is
the advanced autonomy layer with the final lifecycle and self-hosting model:
`observe -> preview -> prepare -> activate` for ordinary repos, plus
`compound-brain` as an always-prepared, always-activated orchestrator source
repo. The first implementation tranche for that model now exists on branch
`codex/activate-repo-mvp`.

## Scope
In scope:
- Global shared runtime in `~/.claude/` for hooks, cron-driven LLM loops, QMD
  sync, cross-project memory, GitHub architecture radar, preview cache, and
  promotion inbox review
- `prepare-brain` flow that creates static project memory and `.codex/AGENTS.md`
  without enabling local autonomy
- `activate-repo` flow that confirms strategic goals, creates repo-local
  `.claude/`, and starts bounded autonomous loops
- Repo-local department agents, action queues, confidence scoring, approvals,
  autoresearch, and skill evolution after activation
- Self-hosting improvement loops for `compound-brain` itself, gated by an
  approval-controlled architecture evaluator

Out of scope for v1:
- Full Codex parity beyond shared file compatibility
- Auto-merge to main
- Hosted remote control plane
- Generalized execution across every language stack on day one

## Current State
- `README.md` and `ARCHITECTURE.md` describe the original compound-brain model
- `install.sh` seeds `~/.claude/`, scripts, knowledge, and hooks
- `scripts/` already contains project audit, intelligence, probability, and
  GitHub intelligence primitives
- `.brain/` was scaffolded on 2026-03-21 for this repo and now holds project
  planning state
- Approved design documents live in `docs/plans/2026-03-21-activate-repo-*.md`
- Advanced autonomy design and implementation plan now define the next runtime
  tranche on branch `codex/activate-repo-mvp`
- The branch now implements preview caching, static brain preparation, activation
  approvals, department state, bounded department cycles, evaluator-backed
  autoresearch execution, local skill promotion, global promotion inbox review
  and approved application, self-hosting evaluator surfaces, and scorecard
  automation
- The current worktree tranche adds a managed global Codex bootstrap through
  `~/.codex/AGENTS.md` plus a scheduled promotion-review runner for the global
  inbox, bringing Claude/Codex runtime alignment and cross-project review loops
  closer to the intended model
- Activated repos now have a shared runtime event engine for session start,
  stop, and cron autoimprovement: audits, intelligence briefs, ranked actions,
  department cycles, and autoresearch can refresh automatically through hooks
  and scheduled dispatch instead of placeholder hook files
- The runtime now records per-repo heartbeats, uses lockfiles to prevent
  overlapping runs, backs off after cron failures, and writes a global watchdog
  report so missed or missing heartbeats are visible
- Activated repos now also build a repo-aware skill inventory that infers
  missing capabilities from stack and departments, searches repo-local and
  global skills first, optionally searches approved external skill roots, and
  tracks active, stale, recommended, and missing skills in `.brain/state/skills.json`
- The activation/runtime branch now adds an autonomy-depth governor with global
  `~/.claude/policy/` seeds, repo-local depth/governor/packet/context files,
  fail-closed preload checks, and depth-aware cron behavior
- The current tranche adds explicit cross-department arbitration plus trust
  history, healthy streaks, and agreement-aware depth movement so operations or
  architecture objections can push higher-depth cron work back into planning
  instead of letting execution continue blindly
- The full branch verification passed: `python3 -m unittest discover -s tests -p
  'test_*.py' -v`, `bash install.sh --dry-run`, and end-to-end preview/prepare/
  activate smoke tests

## Key Concepts
- Shared runtime + per-repo preview/prepare/activate overlay
- Strategic confirmation only for project goal, department goals, major
  architecture changes, and evaluator changes
- Repo-local `.claude/` hooks only after a repo becomes activated
- Department-driven autonomy with confidence/probability-ranked action queues
- Global GitHub architecture radar that improves the orchestrator itself
- Global promotion inbox for cross-project learnings
- Self-hosted orchestrator evaluation for `compound-brain`
- Repo-aware skill discovery and materialization for activated repos
- Policy-driven autonomy depth with trust-governed execution lanes
- Cross-department agreement as a first-class runtime gate

## Key Decisions
- Make the public product an actionable Claude skill run inside a repo
- Keep Claude Code first-class and preserve Codex compatibility via shared files
- Treat ordinary repos as a four-state lifecycle: observe, preview, prepare,
  activate
- Allow strong but bounded execution via isolated branches/worktrees and local
  validation gates
- Enforce a single repo control plane for Claude and Codex through `CLAUDE.md`,
  `.brain/`, and `.claude/`
- Make `compound-brain` always prepared and always activated as the
  self-improving orchestrator source repo

## Risks
- Existing installer/docs still describe a more generic runtime and will drift
  until reworked around the activation skill
- Repo-local hooks and department agents increase complexity if the runtime
  contract is not sharply defined
- Full-autonomy expectations can outpace safe gates if action boundaries are not
  explicit in code and docs
- Self-hosting evaluator drift would make the orchestrator game its own success
  criteria if evaluator changes are not approval-gated

## Next Actions
- Decide how to integrate `codex/activate-repo-mvp`
- Extend department cycles from gated queue handling into richer execution and
  evaluator-aware actions
- Add worktree-isolated experiment mutation around the evaluator-backed
  autoresearch loop
- Improve department-authored global promotion candidates with richer QMP and
  decision payloads
- Tighten self-hosting evaluator coverage beyond the current deterministic
  gates, rubric checks, and smoke canary
- Improve the skill-matching heuristics beyond the current conservative
  title-and-capability filters so repo recommendations stay high-signal as the
  approved external skill inventory grows
- Deepen department execution once the new arbitration and trust-history gates
  have stabilized under more realistic project workloads
- Decide whether to merge `codex/activate-repo-mvp` or keep iterating in branch

## Links
- Repo: /Users/erikfigueiredo/Documents/GitHub/compound-brain
- Design: docs/plans/2026-03-21-activate-repo-design.md
- Plan: docs/plans/2026-03-21-activate-repo.md
