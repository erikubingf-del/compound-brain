# Brain Task Queue

Routines claim a row at start (Status → in_progress, Claimed By → routine name) and mark it done at end. Check this queue at session start; unclaimed high-priority items come first.

| ID | Task | Status | Priority | Claimed By | Notes |
|----|------|--------|----------|------------|-------|
| 001 | Weekly LLM architecture digest (2026-08-03 research + 2026-08-04 bootstrap) | done | high | weekly-digest | Digests in knowledge/research/ (tracked; daily/ is gitignored) |
| 012 | Weekly LLM architecture digest 2026-08-10 | in_progress | high | weekly-digest | Research scan running |
| 002 | CLAUDE.md audit → hierarchical split | proposal-written | high | weekly-digest | Proposal at knowledge/decisions/proposal-002-claude-md-hierarchy.md — NEEDS APPROVAL to apply |
| 003 | validate-digest typed schema skill | done | medium | weekly-digest | knowledge/skills/validate-digest.md |
| 004 | ~~Enable agent checkpointing~~ | cancelled | — | — | Feature claim failed verification against official docs |
| 005 | SAGE novelty gate for memory writes | spec-written | low | weekly-digest | Spec at knowledge/resources/sage-novelty-gate-spec.md — prototype code NEEDS APPROVAL |
| 006 | Delete public branch `claude/cool-heisenberg-2iokix` | pending | high | — | Carries project/host names in an earlier routine draft on a PUBLIC repo; main is clean. Owner action — deleting a pushed branch is outward-facing |
| 007 | Decide repo visibility: public → private | pending | high | — | A brain governing autoresearch, approvals, and autonomy depth on a public repo. Recommend private; see 2026-08-04 digest Needs Approval |
| 008 | Run `/doctor` before queue 002 | pending | medium | — | v2.1.205+ audits CLAUDE.md for derivable content and dedups local vs checked-in; reduces 002 to reviewing its proposals |
| 009 | Verify the plugin loads in a real routine/cloud session | pending | high | — | MUST pass before deleting `.claude/skills/`. Deleting first turns the weekly run into a silent no-op with no error |
| 010 | Delete `.claude/skills/` once 009 passes | blocked-by-009 | medium | — | Separate commit. Superseded by `plugins/compound-brain/skills/` |
| 011 | Keep the Bash allowlist narrow | pending | high | — | The Write/Edit denies do not cover shell writes; the boundary holds only because Bash is limited to git/ls/mkdir. Re-check before adding any Bash rule |
| 012 | Weekly LLM architecture digest 2026-08-10 | done | high | weekly-digest | Digest at knowledge/research/2026-08-10-llm-architecture-digest.md |
| 013 | Audit multi-agent pipelines for agent authority escalation reliance | done | medium | weekly-digest | No hooks directory exists (local or global); no SendMessage calls in any hook. Nothing to fix — clean. |
| 014 | Add Tool(param:value) deny rules for cron session permission hardening | pending | medium | — | e.g. Agent(model:opus) blocks opus spawns in scheduled sessions only; NEEDS APPROVAL for settings change |
| 015 | Trial nested subagent tree (3 levels) in weekly digest research lanes | pending | low | — | Fork 4 research lanes as level-2 subagents, each spawning a verifier at level-3; SAFE to prototype in the routine stored prompt |
| 016 | Enable fallbackModel in settings for scheduled routines | done | medium | weekly-digest | Applied 2026-08-10: fallbackModel ["claude-sonnet-5", "claude-haiku-4-5"] added to .claude/settings.json |
| 017 | Prototype judge-loop refinement step at end of digest generation | pending | medium | — | Run judge agent against validate-digest schema before writing file; implementable with existing subagent primitives in stored prompt — SAFE |
