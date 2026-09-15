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
| 009 | Verify the plugin loads in a real routine/cloud session | blocked-by-016 | high | — | Evidence 2026-08-19: this cloud session loaded skills un-namespaced → from `.claude/skills/`, plugin NOT enabled in cloud sessions. Fix is 016; after it lands, next scheduled run must confirm `compound-brain:*` skills appear |
| 010 | Delete `.claude/skills/` once 009 passes | blocked-by-009 | medium | — | Separate commit. Superseded by `plugins/compound-brain/skills/` (plugin copies are newer — they carry scope checks the legacy copies lack) |
| 011 | Keep the Bash allowlist narrow | pending | high | — | The Write/Edit denies do not cover shell writes; the boundary holds only because Bash is limited to git/ls/mkdir. Re-check before adding any Bash rule |
| 012 | Audit routines and skills for `/ultraplan` references | done | medium | attended-2026-08-19 | Grep clean 2026-08-17 and 2026-08-19 (all hits informational). Re-check only when new skills are added |
| 013 | Tag L0/L1 knowledge in AGENTS.md and knowledge/_index.md | done | medium | attended-2026-08-19 | Must-load tags added to AGENTS.md header and _index.md; see knowledge/resources/mempalace-memory-taxonomy.md (note: source pattern is owner-review-pending) |
| 014 | Evaluate Claude Security plugin on `.claude/` changes | pending | medium | — | Official Anthropic marketplace: `/plugin install claude-security@claude-plugins-official`; requires approval to install and run |
| 015 | Cross-session messaging prototype for brain skills | pending | low | — | brain-orient → SendMessage → brain-write handoff; design compact message format (not context dump); requires interactive multi-session test |
| 016 | OWNER: enable plugin for this repo's cloud sessions | pending | high | — | In an interactive session here run `/plugin marketplace add erikubingf-del/compound-brain` then `/plugin install compound-brain@compound-brain`, choose **Project scope**. Before committing, verify settings carry BOTH `enabledPlugins` AND an `extraKnownMarketplaces` entry (github source) — enabledPlugins alone may not resolve in a fresh cloud clone. Verified steps: knowledge/resources/plugin-enablement.md. Unblocks 009 → 010 |
| 017 | OWNER: merge branch `claude/cool-heisenberg-u6pz4k` to main | pending | high | — | Carries the 2026-08-17 digest + 2026-08-19 apply-lane upgrade. Until merged, next scheduled run (fresh clone of main) cannot see them and dedup breaks |
| 018 | OWNER: install plugin at user scope on workstation | pending | medium | — | Same two commands, **User scope** — loads brain skills in ALL local projects; enable marketplace auto-update (`/plugin` → Marketplaces → compound-brain) so every push propagates. See knowledge/resources/plugin-enablement.md |
