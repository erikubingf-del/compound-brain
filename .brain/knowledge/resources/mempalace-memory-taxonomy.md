# MemPalace Memory Taxonomy — Extractable Pattern

**Source:** [multi-agent-ralph-loop](https://github.com/alfredolopez80/multi-agent-ralph-loop) (third-party, patterns extracted natively — do not install or execute external code)
**Logged:** 2026-08-17

---

## Core Insight

"Selection beats encoding" — loading only the right rules at session start outperforms loading all rules in a compressed form. A 4-layer stack separates what must load at startup from what loads on demand.

---

## 4-Layer Stack

| Layer | What It Contains | Load Timing | Token Budget |
|-------|-----------------|-------------|--------------|
| L0 | Agent identity + inviolable principles | Always, session start | ~818 tokens |
| L1 | Actionable rules filtered from full corpus | Always, session start | Small; high signal-to-noise |
| L2 | Project-specific taxonomy (halls/rooms/wings) | On-demand per task | Medium; domain-scoped |
| L3 | Full knowledge base (wiki, research, resources) | On-demand by query | Large; query-time only |

---

## Mapping to This Brain

| MemPalace Layer | Brain Equivalent | Notes |
|----------------|-----------------|-------|
| L0 | `.brain/AGENTS.md` (top section) + `CLAUDE.md` operating rules | Identity and invariants that every run needs |
| L1 | `.brain/AGENTS.md` (learnings log) + `.brain/queue.md` (current tasks) | Actionable state; must-read per run |
| L2 | `.brain/knowledge/projects/` + `.brain/knowledge/decisions/` | Domain facts; load when working in that domain |
| L3 | `.brain/knowledge/` full tree | Load on query; never preload at session start |

---

## Implementation Notes

- Mark L0/L1 documents with a `must-load: true` comment at the top — makes the session-start read list explicit.
- L2 files should be scoped: `.brain/knowledge/departments/<dept>.md` loads only when that department leads the session.
- L3 should only be queried, never bulk-read; the weekly digest already follows this pattern (reads last 4 digests, not all of them).
- The 818-token target for L0 is a useful ceiling: if AGENTS.md identity section plus CLAUDE.md startup rules exceed that, prune or move to L1.

---

## Related Queue Items

- Queue 013: Tag L0/L1 knowledge in AGENTS.md and knowledge/_index.md for tiered loading
- Queue 002: CLAUDE.md audit — splitting hierarchically already moves content from L0 to L2/L3
