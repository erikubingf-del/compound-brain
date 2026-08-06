# Candidate skills — drafts awaiting promotion

The weekly digest routine may write proposed skills here as
`<skill-name>/SKILL.md`. This directory sits under `.brain/`, so writing here
is SAFE under the existing rule and needs no permission change.

**Nothing here is loaded by Claude Code.** These are inert drafts. A skill only
becomes live when a human promotes it into `plugins/compound-brain/skills/`.

## Why the gate exists

The routine's inputs are pages on the open web, fetched by an unattended job.
Content under `plugins/**` executes as instructions in every project where the
plugin is enabled. The distance between "markdown a robot wrote after reading a
blog" and "instructions injected into every repo I own" is the entire security
model of this system, and the promotion step is that distance.

This is also why the routine may not write to `plugins/**` or
`.claude/skills/**` directly. An unattended run that can edit its own
instructions is not constrained by them.

## Promoting a draft

1. **Read it in full.** Not skim — read. It came from the internet by way of a
   summarizer.
2. Check it against the rules in `brain-write`: no project, service, host, or
   strategy names; this repo is public and git history is permanent.
3. Confirm it degrades gracefully in a project with no `.brain/` tree — plugin
   skills load everywhere, including repos that have never heard of this one.
4. Move it to `plugins/compound-brain/skills/<name>/SKILL.md`.
5. Verify the frontmatter has `name` and a `description` that says both what it
   does and when to trigger.
6. Commit. Since the plugin deliberately carries no `version`, the commit SHA
   is the version and the push is the release.

## Rejecting a draft

Delete it and append one line to `.brain/AGENTS.md` saying what was rejected and
why. A rejection that leaves no trace gets re-proposed next month.
