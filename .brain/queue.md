# Brain Task Queue

Routines claim a row at start (Status → in_progress, Claimed By → routine name) and mark it done at end. Check this queue at session start; unclaimed high-priority items come first.

| ID | Task | Status | Priority | Claimed By | Notes |
|----|------|--------|----------|------------|-------|
| 001 | Weekly LLM architecture digest (2026-08-03 research + 2026-08-04 bootstrap) | done | high | weekly-digest | Digests in knowledge/research/ (tracked; daily/ is gitignored) |
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
| 012 | Weekly LLM architecture digest 2026-11-16 | done | high | weekly-digest | Digest at knowledge/research/2026-11-16-llm-architecture-digest.md |
| 013 | Audit brain skills for Task tool usage | pending | high | — | TaskCreate/TaskUpdate/TodoWrite removed on Sonnet 5+/Fable 5+; grep .claude/ plugins/ .brain/ — no code writes needed for audit |
| 014 | Run /skill-doctor on compound-brain plugin | pending | medium | — | Identifies dead-weight skills inflating context; read-only; attended session |
| 015 | Draft eval suite for brain-digest skill via claude plugin eval | pending | medium | — | SAFE — markdown writes under .brain/; `claude plugin eval init` drafts cases |
| 016 | Add permissions.denyInsteadOfPrompting to routine settings | pending | medium | — | NEEDS APPROVAL — settings file change; prevents unattended runs from hanging on blocked tool calls |
| 017 | Audit injected context layer size | pending | low | — | Ensure .brain memory files loaded at session start are under ~2k tokens each; SAFE read-only audit |
| 018 | Design dreaming pass for .brain memory consolidation | pending | low | — | Write spec as knowledge/resources/dreaming-pass-spec.md (SAFE); implementing as cron NEEDS APPROVAL |
