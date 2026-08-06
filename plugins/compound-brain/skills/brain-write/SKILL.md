---
name: brain-write
description: Route a fact, decision, pattern, or learning into its correct home in the .brain/ knowledge tree instead of inventing a new ad-hoc file for it. Use this whenever the user says "save this", "remember this", "add this to the brain", "log this decision", "write this up", "make a note", or whenever you finish work that produced a reusable insight worth keeping. Covers the routing rules (project fact vs resource vs decision vs daily note vs AGENTS.md vs queue), the append-only conventions, the index update, and the public-repo scrub rule. Prefer this over creating files under .brain/ by hand.
---

## Scope check — run this first

This skill is installed via a plugin, so it loads in **every** project, but it
operates on a `.brain/` knowledge tree that only brain-activated repos have.

Before doing anything else, check whether `.brain/` exists in the current
working directory.

- **`.brain/` exists** — proceed normally; everything below applies.
- **`.brain/` is absent** — this project is not brain-activated. Say so plainly
  and stop. Offer to scaffold it, but do not create files unasked: silently
  starting a second, empty brain in an unrelated repo is worse than doing
  nothing, because it looks like memory while holding none.

Never write `.brain/` content into a repo that did not already have one without
the owner asking for it.

# Write into the brain, in the right place

The failure mode this prevents is not "losing information" — it is
information landing somewhere nobody will look again. A brain with six
overlapping places to record a decision is a brain where no place is
authoritative. Route first, then write.

## Routing table

Match what you have to where it goes:

| What you have | Where it goes |
|---|---|
| A fact about this project's state | `.brain/knowledge/projects/compound-brain.md` |
| A reusable pattern, spec, or technique | `.brain/knowledge/resources/<topic>.md` |
| A pattern reusable across *other* projects too | `~/.claude/knowledge/` (global, not this repo) |
| A strategic rule or architectural choice | `.brain/knowledge/decisions/log.md` |
| A proposal that needs approval before acting | `.brain/knowledge/decisions/proposal-<id>-<slug>.md` |
| Today's working trail | `.brain/knowledge/daily/YYYY-MM-DD.md` (gitignored — local only) |
| A research digest | `.brain/knowledge/research/YYYY-MM-DD-llm-architecture-digest.md` |
| A lesson a future *routine* run needs | `.brain/AGENTS.md` (append-only) |
| A task someone should pick up later | `.brain/queue.md` |
| A capability or skill change | `.brain/knowledge/skills/skill-graph.md` |

Two distinctions people get wrong:

**Decision vs. resource.** A decision records *what we chose and why*, and is
binding. A resource records *how something works*, and is reference. If a
future session could reasonably do the opposite without it being a mistake,
it is a resource, not a decision.

**AGENTS.md vs. daily note.** `AGENTS.md` is for lessons that change how a
future automated run behaves. A daily note is for narrative. If it would not
change anyone's behavior, it is not an AGENTS.md entry — that file's value
decays fast if it fills with color.

## Conventions that matter

**Append-only where it says append-only.** `.brain/AGENTS.md` and the
decisions log accumulate; do not rewrite prior entries. If something is now
wrong, append a dated correction beneath it. The history of what was believed
and when is part of the value.

**Update the index.** New file under `.brain/knowledge/` means a line in
`.brain/knowledge/_index.md`. Unindexed files are invisible to the next
session.

**Do not duplicate.** Before appending, grep for the same fact, URL, or
decision. If it already exists and you are adding detail, edit the existing
entry in place with a dated line rather than adding a near-duplicate. If it
already exists and you are adding nothing, skip it and say so. Files that
grow by repetition stop being read.

## This repo is public — scrub before writing

`erikubingf-del/compound-brain` is a public repository, and git history is
permanent: scrubbing a name in a later commit does not remove it from
history. Never write project, service, host, strategy, or account names into
anything under `.brain/`. Use the generic category instead — "the live
trading project", "cloud infrastructure", "the private stored prompt".

If you are unsure whether a name is sensitive, leave it out and say what you
omitted. Omitting a name costs a follow-up question; publishing one cannot be
undone.

## What needs approval

Writing markdown under `.brain/**` is safe and needs no approval. These are
different and must be proposed, not done: `CLAUDE.md` or `core/BRAIN.md`
content, hooks, scripts, cron, MCP config, settings, `.gitignore`, and
anything touching live production or funds-handling systems. When the right
answer is one of those, write the proposal into
`.brain/knowledge/decisions/` and say plainly that applying it needs a
decision.
