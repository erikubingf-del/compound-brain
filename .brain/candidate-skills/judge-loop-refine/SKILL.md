# Candidate Skill: Judge-Loop Refinement

**Status:** draft — human review required before promotion to `plugins/`
**Source:** Simmer pattern (awesome-claude-code-toolkit, 2026-08-10 digest), reimplemented natively
**Risk:** SAFE to draft here; promotion to plugins/** requires approval

---

## What This Skill Does

Runs a multi-round iterative refinement loop on any artifact:

1. Generate initial draft (or receive one as input)
2. Spawn a judge subagent that evaluates the draft against an explicit rubric file
3. If judge score < threshold: revise draft based on feedback, go to step 2
4. If judge score >= threshold OR max rounds reached: write final artifact

The stopping condition is an externalized rubric, not the generator's self-assessment.

---

## Usage

```
/judge-loop-refine <artifact-path> <rubric-path> [max-rounds=3] [threshold=80]
```

- `artifact-path`: path to file to refine (or `stdin` to read from conversation)
- `rubric-path`: path to a markdown file listing scored criteria (0–100 per criterion)
- `max-rounds`: max refinement iterations before writing regardless of score (default 3)
- `threshold`: minimum aggregate score to stop early (default 80 out of 100)

---

## Rubric File Format

```markdown
# Rubric: <artifact type>

## Criteria

| Criterion | Weight | Score (0–100) | Notes |
|-----------|--------|--------------|-------|
| Required sections present | 30 | | |
| No unverified claims implemented | 25 | | |
| Actionable recommendations | 20 | | |
| No prior-digest duplicates | 15 | | |
| Risk tags present on all AUTO-APPLY items | 10 | | |

## Aggregate score: [weighted average]
## Verdict: PASS (>=80) / REVISE (<80)
## Revision notes: [specific items to fix]
```

---

## Implementation Notes

- Judge subagent runs in foreground (needs result before continuing)
- Use `/goal "aggregate score >= {threshold} or rounds exhausted"` as the loop termination condition
- Generator and judge use separate subagent context windows; generator never sees judge's evaluation of prior rounds directly — only the revision notes extracted from the rubric output
- SAFE: all I/O is file reads/writes under `.brain/`; no external service calls

---

## Application to Weekly Digest

Rubric: `validate-digest.md` (already exists at `.brain/knowledge/skills/validate-digest.md`) extended with scoring weights.

Expected benefit: malformed or schema-violating digests caught before git commit; no silent dedup failures on next run.

---

## Promotion Checklist (human review)

- [ ] Review rubric format for edge cases
- [ ] Verify judge prompt does not introduce hallucination of scores
- [ ] Test in a sandboxed session before enabling for scheduled runs
- [ ] Approve promotion to `plugins/compound-brain/skills/judge-loop-refine/`
