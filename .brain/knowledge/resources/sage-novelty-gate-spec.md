# SAGE Novelty Gate — Design Spec (queue 005)

Source pattern: https://arxiv.org/abs/2605.30711 (SAGE, May 2026). Status: spec only — prototype code is NEEDS APPROVAL.

## Problem

Long-running brains bloat their memory stores because every run appends. Nearly all memory tooling optimizes the read side (retrieval); the write side is unguarded.

## Pattern

A write-side gate classifies every candidate memory entry before it lands:
- **ADD** — novel relative to existing entries → append.
- **NOOP** — redundant → discard.
- **MERGE** — uncertain → route to an explicit merge step against the nearest existing entry.

SAGE implements this with a von Mises–Fisher density estimator over memory embeddings, with a self-calibrating threshold that tracks the store's geometry as it grows. Reported: 3.4× write-phase API cost reduction, 2.5× latency reduction, minimal quality loss.

## Brain-native reimplementation (no third-party code)

The brain's memory is markdown, not vectors — a faithful lightweight analog:

1. **Gate location:** the "append learnings to AGENTS.md" and "update knowledge/" steps of every routine.
2. **ADD/NOOP check:** before appending, grep the target file (and _index.md) for the same fact/URL/decision. Exact or near matches → NOOP with a one-line note in the run log.
3. **MERGE check:** if a candidate overlaps an existing entry but adds detail (new outcome, corrected number, superseding decision), edit the existing entry in place (append a dated correction line) instead of adding a duplicate.
4. **Threshold analog:** as a file grows past ~150 lines, tighten the gate — require a candidate to change a decision or outcome, not just add color.

## Success criteria

- AGENTS.md and decision log grow by facts, not repetition.
- No duplicate Top Finds across consecutive digests (dedup rule holds).
- If a vector store is ever added to the brain, revisit this spec and implement the density-estimator gate properly — at that point prototype code needs approval.
