# Candidate Skill: Plugin Eval Quality Gate

**Status:** draft — not promoted to plugin; human review required before promotion
**Drafted:** 2026-11-09 by weekly-digest routine
**Source:** `claude plugin eval` — [VERIFIED: official docs w37, code.claude.com/docs/en/whats-new/2026-w37]

---

## Pattern Description

Before promoting a candidate skill from `.brain/candidate-skills/<name>/SKILL.md` to the
compound-brain plugin, run a with/without eval to measure whether the skill actually improves
Claude's output vs. just consuming context budget.

## When to Use

Run this pattern when:
- A candidate skill has been drafted and the author wants to promote it
- An existing plugin skill is suspected of over-triggering or adding cost without value
- Preparing a new plugin release

## Steps

1. From the compound-brain plugin root, run:
   ```bash
   claude plugin eval init
   ```
   Claude opens an interactive session and asks what a good result looks like.
   Describe 5–7 intents: when should the skill fire, what should it produce, when should it NOT fire.

2. Claude drafts test cases and graders. Exit when it says the suite is ready.

3. Run the eval:
   ```bash
   claude plugin eval .
   ```
   Each case runs with and without the plugin. The summary table shows a delta score.

4. Interpret results:
   - Positive delta (plugin improves output): proceed to promotion
   - Zero or negative delta: skill costs context without benefit; revise or drop it
   - High false-trigger rate: narrow the skill's trigger conditions

5. Save the `evals/` folder in `.brain/candidate-skills/<name>/` for future reference.

## Notes

- Each eval run makes real model calls on your account
- Do NOT run this in a scheduled routine — it requires interactive session setup
- Do NOT promote a skill with a negative delta; the brain's context budget is finite
- `evals/results/report.html` has per-run detail
