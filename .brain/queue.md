# Brain Task Queue

Routines claim a row at start (Status → in_progress, Claimed By → routine name) and mark it done at end. Check this queue at session start; unclaimed high-priority items come first.

| ID | Task | Status | Priority | Claimed By | Notes |
|----|------|--------|----------|------------|-------|
| 001 | Weekly LLM architecture digest (2026-08-03 research + 2026-08-04 bootstrap) | done | high | weekly-digest | Digests in knowledge/research/ (tracked; daily/ is gitignored) |
| 002 | CLAUDE.md audit → hierarchical split | proposal-written | high | weekly-digest | Proposal at knowledge/decisions/proposal-002-claude-md-hierarchy.md — NEEDS APPROVAL to apply |
| 003 | validate-digest typed schema skill | done | medium | weekly-digest | knowledge/skills/validate-digest.md |
| 004 | ~~Enable agent checkpointing~~ | cancelled | — | — | Feature claim failed verification against official docs |
| 005 | SAGE novelty gate for memory writes | spec-written | low | weekly-digest | Spec at knowledge/resources/sage-novelty-gate-spec.md — prototype code NEEDS APPROVAL |
