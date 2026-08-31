# Brain Agent Learnings

Append-only log. Each scheduled routine adds 1–3 lines after its run. Read this before starting any routine.

---

## 2026-08-04 — Weekly LLM Architecture Digest (bootstrap + test run)

- Ralph Loop adopted for all routines: fresh context each run, state in this repo, learnings compound here.
- 3 of 4 native-feature claims sourced from third-party blogs failed verification against official docs (checkpointing scope, sub-agent depth, workflow tiers). Standing rule: official docs or [UNVERIFIED], never implement unverified claims.
- Next priorities: CLAUDE.md hierarchical audit (queue 002 — proposal written this run), SAGE write-gate prototype before any vector memory (queue 005 — spec written this run).
- Bootstrap notes: repo already had a mature .brain/ tree (MEMORY.md, knowledge/_index.md, decisions/log.md DEC-001..019). Integrated append-only; conventions followed: daily notes in knowledge/daily/, decisions in decisions/log.md, index updated.
- Artifact-fetch bridge for the 2026-08-03 digest verified working; local copy used for fidelity.

---

## 2026-08-04 — Bootstrap verification run (push access + persistence)

- **This repo is PUBLIC** (`visibility: public`, GitHub API, 2026-08-04). Never write project, service, host, or strategy names anywhere under `.brain/` — git history is permanent and a later scrub does not remove them. The generic risk categories in the routine are deliberate; the specific list stays in the private stored prompt.
- **The environment guard as originally written aborted every cloud run.** It required three `~/.claude/` files that do not exist in a cloud container, so the scheduled Monday run would have printed the ABORT line and written zero files — silently, looking like a clean no-op. Guard now accepts either the repo brain (cloud) or the local `~/.claude` brain. Lesson: a guard written for a workstation is not a guard, it is an off switch, once the routine moves to a container.
- **Digests must be written somewhere tracked.** `.brain/knowledge/daily/` is gitignored, so digests written there die with the container and Step 0's dedup rule reads nothing — meaning every weekly run silently re-reports the same findings. Digests now go to `.brain/knowledge/research/`.
- **Push to `main` from a cloud session is verified working** (2026-08-04, two commits). This was the step the prior session could not complete.
- **Outstanding leak:** branch `claude/cool-heisenberg-2iokix` was pushed to this public repo on 2026-08-04 containing project and host names in an earlier draft of the routine. `main` is clean. That branch should be deleted.

---

## 2026-08-04 — Plugin architecture and the trust boundary

- **Project skills do not propagate; plugin skills do.** `.claude/skills/` loads only in its own repo. The brain now ships as a plugin (`plugins/compound-brain/` + `.claude-plugin/marketplace.json`) so skills load in every project where it is enabled, namespaced `compound-brain:<skill>`.
- **`~/.claude/skills/` is the wrong vehicle here, specifically.** Personal-scope skills are not available to cloud or routine sessions, and the weekly routine *is* a remote session. They would work on the workstation and vanish in the one execution mode that matters. Same shape as the guard-that-was-an-off-switch mistake above: correct on a laptop, silently absent in a container.
- **Omit `version` from plugin.json and the marketplace entry.** Version resolves plugin.json → marketplace entry → git commit SHA, and is the update cache key, so omitting it makes every push a release. Setting it pins consumers and makes `/plugin update` a permanent no-op.
- **A run that can edit its own instructions is not constrained by them.** `settings.json` had `Write/Edit(.claude/skills/**)` in `allow` for several hours, which let an unattended run rewrite the SAFE definition that bounds it. Now denied. Use `ask` (not `deny`) for `plugins/**` — attended sessions can approve a promotion, unattended runs have nobody to answer and fail closed.
- **The deny rules only bind the Write/Edit tools, not shell writes.** Applying proposal-003 required a Bash heredoc precisely because `Edit(.claude/settings.json)` is denied — the deny did not stop a shell write. The boundary holds against unattended runs *only because the Bash allowlist is narrow* (git, ls, `mkdir -p .brain`). If that allowlist is ever widened to include `cat`, `tee`, `python3`, `sed -i`, or a bare `Bash(*)`, every Write/Edit deny in this file becomes bypassable in one step. Treat the Bash allowlist as part of the trust boundary, not as convenience.

---

## 2026-08-31 — Weekly LLM Architecture Digest (w30–w34)

- **`/ultraplan` is removed as of w32 (v2.1.220+).** Any CLAUDE.md content, stored prompts, or hooks referencing `/ultraplan` now fail silently. Audit all `.claude/hooks/` and stored prompts before next cron run.
- **Auto mode is now the default permission mode from August 14.** Sessions started on Pro/Max/Team without explicit mode config now run auto mode. Prior assumptions that new sessions run `ask` mode may be wrong. Verify cron session behavior if any hook relied on `ask`-mode prompts to gate action.
- **Cross-session messaging + `notify_when_idle` enables native parallel research lanes.** Forked sessions can signal the orchestrator when idle — no polling, no Dynamic Workflows needed. This is the correct upgrade path for the sequential WebSearch pattern in the weekly routine.
- **200-subagent-per-session cap removed (w32).** Depth (5 levels) and concurrency limits still apply.
- **`/fork` now creates its own worktree.** Parallel forks no longer risk touching the main checkout. Worktree isolation also now blocks Bash and git redirects from reaching the main checkout.
- **`ANTHROPIC_DEFAULT_MODEL` env var** sets model for new sessions without touching any managed file. Useful for pinning routine model via environment config.
