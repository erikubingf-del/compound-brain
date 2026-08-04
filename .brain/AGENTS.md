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
