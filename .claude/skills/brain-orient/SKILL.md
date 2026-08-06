---
name: brain-orient
description: Orient in the compound-brain repo by reading its current state before doing anything else. Reads .brain/AGENTS.md (cross-run learnings), .brain/queue.md (pending work), and the most recent research digests, then reports what is pending, what is stale, and what the last run learned. Use this whenever the user asks "what's the state of the brain", "catch me up", "what should I work on", "what's in the queue", or opens work in this repo without saying what they want — and before any non-trivial change under .brain/, so you build on prior runs instead of silently repeating them.
---

# Orient in the brain

This repo is a live personal brain: its value is that each session starts
where the last one stopped. That only works if you actually read the prior
state. Skipping this is how a brain quietly degrades into a pile of markdown —
every run re-deriving what the last run already figured out.

Read these four things before acting. They are small on purpose.

## 1. Cross-run learnings — `.brain/AGENTS.md`

Append-only log. The most recent entries matter most; they carry standing
rules discovered the hard way (verification requirements, environment
gotchas, leak rules). Treat these as binding, not as history.

## 2. Pending work — `.brain/queue.md`

Table of `ID | Task | Status | Priority | Claimed By`. Look for unclaimed
high-priority rows. If you are about to start work and a higher-priority
unclaimed item exists that falls inside what you are allowed to touch,
raise it rather than silently working on something else.

If you take a row, set Status to `in_progress` and Claimed By to who you
are; mark it done when you finish. A queue nobody updates is worse than no
queue, because it reads as authoritative while being wrong.

## 3. Recent research — `.brain/knowledge/research/`

The last few `YYYY-MM-DD-llm-architecture-digest.md` files. These carry
findings with `confidence` and `outcome` fields. Two reasons to read them:
you avoid re-reporting a known finding, and you can update `outcome` on
items that have since proven out or failed.

If this directory is empty or missing, that is a signal — it means a prior
run failed to push, not that nothing was ever found. Say so.

## 4. Project state — `.brain/MEMORY.md` and `.brain/knowledge/_index.md`

The index is the map of what exists. If you add something to the knowledge
tree, add it to the index too, or it becomes invisible to the next session.

## Report what you found

Give the user a short, concrete orientation, not a file dump:

- what the last run learned that changes what you would do now
- what is pending and unclaimed, highest priority first
- anything stale, missing, or contradictory

## Check the contract against reality

`CLAUDE.md` describes surfaces that may not exist yet — `.brain/state/`,
`.brain/memory/`, `.claude/hooks/`, `.claude/departments/`. When a protocol
tells you to read a file that isn't there, that is a real finding worth
reporting, not something to route around silently. A session-start protocol
that no-ops looks identical to one that succeeded, which is exactly why it
goes unnoticed.

Note that `.brain/memory/*.md` and `.brain/knowledge/daily/` are gitignored
by design, so they are legitimately absent in a fresh clone or a cloud
container. Absent-by-design and absent-by-accident are different findings —
check `.gitignore` before calling something broken.
