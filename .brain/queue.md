# Brain Task Queue

Agents: claim a row (set Status=in_progress, Claimed By=routine-name) at start, mark done at end.
Check-queue: if a higher-priority pending item exists, handle it before your planned work.

| ID | Task | Status | Priority | Claimed By |
|----|------|--------|----------|------------|
| 002 | CLAUDE.md hierarchical audit proposal — falsifiability pass, split into root + per-dir | pending | high | — |
| 003 | validate-digest schema skill — markdown skill that checks required sections/fields in digest files | pending | medium | — |
| 005 | SAGE novelty-gate prototype — density-estimator write-gate for .brain/knowledge/ before any vector memory | pending | low | — |
| 006 | Run /doctor audit — get its CLAUDE.md proposals before starting queue-002 manual audit; review output only, approve fixes separately | pending | high | — |
