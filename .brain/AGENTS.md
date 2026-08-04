# Brain Agent Learnings

Append-only log. Each scheduled routine adds 1–3 lines after its run. Read this before starting any routine.

---

## 2026-08-04 — Weekly LLM Architecture Digest (bootstrap + test run)

- Ralph Loop adopted for all routines: fresh context each run, state in this repo, learnings compound here.
- 3 of 4 native-feature claims sourced from third-party blogs failed verification against official docs (checkpointing scope, sub-agent depth, workflow tiers). Standing rule: official docs or [UNVERIFIED], never implement unverified claims.
- Next priorities: CLAUDE.md hierarchical audit (queue 002 — proposal written this run), SAGE write-gate prototype before any vector memory (queue 005 — spec written this run).
- Bootstrap notes: repo already had a mature .brain/ tree (MEMORY.md, knowledge/_index.md, decisions/log.md DEC-001..019). Integrated append-only; conventions followed: daily notes in knowledge/daily/, decisions in decisions/log.md, index updated.
- Artifact-fetch bridge for the 2026-08-03 digest verified working; local copy used for fidelity.
