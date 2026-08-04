# Skill: validate-digest

Typed-contract validator for weekly LLM architecture digests. Run after writing any digest, before committing. A digest that fails validation must be fixed in the same run — never commit a failing digest.

## Contract (schema v1.0)

Required sections, in order:
1. `## Top Finds` — markdown table; every row must have: name, description, URL (or `—` with an [UNVERIFIED] tag), classification (ADOPT/TEST/WATCH/SKIP)
2. `## Patterns Worth Knowing` — 2–5 entries
3. `## Brain Upgrade Opportunities`
4. `## AUTO-APPLY QUEUE` — every item risk-tagged SAFE or NEEDS APPROVAL
5. `## Recommended Actions` — 1–3 items
6. `## Needs Approval` — may be empty, must exist

## Validation rules

- Every ADOPT/TEST item referencing a native Claude Code feature carries `[VERIFIED: <official url>]` or `[UNVERIFIED]`. `[UNVERIFIED]` items must not appear in AUTO-APPLY QUEUE as SAFE.
- SAFE means: markdown creates/appends/renames under `.brain/**` only. Anything touching live production systems, funds-touching services, cloud infrastructure, hooks, scripts, cron, MCP config, settings, or CLAUDE.md content is NEEDS APPROVAL — no exceptions. (The private routine rules hold the specific project list.)
- Claims without citations are tagged `gap`, not passed forward as fact.
- Each Top Finds entry should carry `confidence` (low/medium/high) and `outcome` (pending/confirmed/invalidated); the next weekly run updates outcomes on prior digests.

## On failure

State which rule failed and fix the digest before committing. If a fix is impossible (e.g., a claim can't be verified), downgrade the item (ADOPT→TEST/WATCH, SAFE→NEEDS APPROVAL) rather than deleting the finding.
