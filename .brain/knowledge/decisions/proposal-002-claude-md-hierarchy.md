# Proposal 002 — CLAUDE.md Hierarchical Split (NEEDS APPROVAL)

Status: proposal only. CLAUDE.md content changes are outside the SAFE allowlist; nothing has been modified.

## Current state

Root `CLAUDE.md` is 357 lines: a managed activation block (lines 1–15) plus the full "Claude Code Operating Contract" (identity, runtime, lifecycle, session protocols, event model, departments, skill intelligence, radar, approvals, autoresearch, knowledge system, session end, auto-improvement).

The progressive-disclosure guideline (2026-08-03 digest, ADOPT): root ≤200 lines / ≤5% of session context, every rule falsifiable ("would Claude err in a real session without this line?"), domain detail pushed to per-directory files loaded only when relevant.

## Proposed split

**Keep in root (~140 lines):** managed block; Identity; Project Brain Location (the OVERRIDE rules); Session Start Protocol; Approvals, Trust, And Depth; Session End Protocol; Core Principle. These are the rules Claude would actually err without in any session.

**Move out (loaded on demand):**
- Departments → `.claude/departments/README.md` (already the departments' home)
- Skill Intelligence + Global Skill Radar → `.brain/knowledge/skills/skill-intelligence.md` (beside skill-graph.md)
- Autoresearch → `.brain/knowledge/areas/autoresearch.md`
- Knowledge System details → already largely duplicated by `.brain/knowledge/_index.md`; keep one pointer line in root
- Event Model + Repo Lifecycle → `.brain/knowledge/areas/runtime-lifecycle.md`
- Auto-Improvement Protocol → `.brain/knowledge/areas/auto-improvement.md`

Each moved section is replaced in root by a one-line pointer.

## Falsifiability audit to run on approval

Walk the remaining root rules; delete any line that fails "would Claude err without this?" Candidates for deletion: restatements of defaults (e.g., "read state first" appears in both Operating Rule and Session Start Protocol — keep one).

## Sync note

Root notes it is derived from `core/BRAIN.md`. The split must be applied to `core/BRAIN.md` first, then re-derived, or the two drift.
