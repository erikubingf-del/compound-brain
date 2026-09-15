# compound-brain — Knowledge Index
_Last updated: 2026-08-19_

<!-- must-load: L1 map — this file is the map of what exists; load listed files on demand (L2/L3), never bulk-read the tree -->

## Projects
- [compound-brain.md](projects/compound-brain.md) — Main project state

## Areas
- [deployment.md](areas/deployment.md) — Deployment rules

## Resources
- [sage-novelty-gate-spec.md](resources/sage-novelty-gate-spec.md) — Write-side memory gate design (queue 005)
- [mempalace-memory-taxonomy.md](resources/mempalace-memory-taxonomy.md) — Tiered L0–L3 memory loading pattern (extracted natively)
- [plugin-enablement.md](resources/plugin-enablement.md) — Verified steps to enable brain skills in all projects + cloud sessions, and how updates propagate

## Skills
- [skill-graph.md](skills/skill-graph.md) — Project skill map
- [validate-digest.md](skills/validate-digest.md) — Contract notes
- **Canonical loadable skills live in `plugins/compound-brain/skills/`** — `brain-orient`, `brain-write`, `brain-digest`, `validate-digest` (namespaced `compound-brain:*` where the plugin is enabled; see resources/plugin-enablement.md). `.claude/skills/` holds older un-namespaced copies that still serve sessions in this repo until queue 009/010 retire them.

## QMP
- [_index.md](qmp/_index.md) — Project QMP library

## Decisions
- [log.md](decisions/log.md) — Strategic decisions
- [proposal-002-claude-md-hierarchy.md](decisions/proposal-002-claude-md-hierarchy.md) — CLAUDE.md split proposal (NEEDS APPROVAL)

## Daily Notes
- Stored in `daily/YYYY-MM-DD.md`
- Weekly LLM architecture digests: `research/YYYY-MM-DD-llm-architecture-digest.md` — tracked in git, unlike `daily/` (routine: `../routines/weekly-digest-prompt.md`)

## Weekly Reviews
- Stored in `weekly/YYYY-MM-DD.md`
