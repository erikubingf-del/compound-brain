---
name: validate-digest
description: Validate a compound-brain research digest against its typed contract before it gets committed. Checks required sections and order, Top Finds row fields, VERIFIED/UNVERIFIED tags on native-feature claims, SAFE vs NEEDS-APPROVAL risk tags in the auto-apply queue, confidence/outcome fields, and the public-repo name scrub. Use right after writing or editing any file under .brain/knowledge/research/, before committing a digest, and whenever the user asks to check, validate, or lint a digest. Catches malformed digests at the boundary instead of letting the next weekly run inherit them.
---

# Validate a digest

A digest is a typed handoff between weekly runs, not free-form prose. Next
week's run reads it to dedup findings and update outcomes, so a malformed
digest does not fail loudly — it quietly degrades every future run. Catching
it here is the whole point.

Validate the target file (default: the newest file in
`.brain/knowledge/research/`) against the contract below, then report pass or
fail with the specific rule and line.

## Contract, schema v1.0

Required sections, in this order:

1. `## Top Finds` — a markdown table
2. `## Patterns Worth Knowing` — 2–5 entries
3. `## Brain Upgrade Opportunities`
4. `## AUTO-APPLY QUEUE` — every item risk-tagged
5. `## Recommended Actions` — 1–3 items
6. `## Needs Approval` — may be empty, must exist

`Needs Approval` must exist even when empty. An absent section is ambiguous
between "nothing needed approval" and "nobody checked"; an empty one is not.

## Row rules for Top Finds

Every row carries: name, description, URL, classification
(ADOPT/TEST/WATCH/SKIP), `confidence` (low/medium/high), and `outcome`
(pending/confirmed/invalidated).

A missing URL is acceptable only as `—` alongside an `[UNVERIFIED]` tag —
that combination says "we could not source this", which is a legitimate
finding. A missing URL with no tag is a citation gap: flag it.

## Verification rules

Any item referencing a native Claude Code feature must carry
`[VERIFIED: <official url>]` or `[UNVERIFIED]`. The verifying URL has to be
official — `code.claude.com` or `anthropic.com`. A third-party blog cited as
`[VERIFIED:...]` is a failure, and it is the failure this rule exists for.

An `[UNVERIFIED]` item must never appear in the AUTO-APPLY QUEUE tagged SAFE.

## Risk tags

Every AUTO-APPLY item is tagged SAFE or NEEDS APPROVAL.

SAFE is narrow: markdown creates, appends, and renames under `.brain/**`.
Anything touching live production or funds-handling services, cloud
infrastructure, hooks, scripts, cron, MCP config, settings, `.gitignore`, or
`CLAUDE.md` content is NEEDS APPROVAL. An item tagged SAFE that touches any
of those is the most serious failure this validator catches — it is the one
that would cause an unattended run to do something it should have asked about.

## Public-repo scrub

This repo is public. Scan for project, service, host, strategy, and account
names. Generic categories are correct; specifics belong in the private stored
prompt. Since git history is permanent, this check only helps before the
commit — flag any hit as blocking.

## Reporting

State pass, or name the rule that failed and where. Then fix it in the same
run — a validator whose findings are noted and not acted on has done nothing.

When a fix is impossible, downgrade rather than delete: ADOPT becomes
TEST or WATCH, SAFE becomes NEEDS APPROVAL. Deleting a finding you could not
verify loses information; downgrading keeps it with an honest label.
