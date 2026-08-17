# LLM Architecture Digest: 2026-08-17

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** 4-lane scan covering Weeks 30–32 (July 20 – August 7, 2026) plus GitHub trending and community lane. Prior digests covered through Week 29; all items below are new.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | Cross-Session Messaging | Sessions on the same machine can now message each other via `ListAgents` + `SendMessage`. Text only (not history or files). One session asks another to pass along a finding or a decision. macOS and Linux, v2.1.224+. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 2 | Auto Mode Becomes Default (Aug 14) | Auto mode is now the default permission mode for new sessions on Pro, Max, and Team plans. Classifier calls no longer count toward usage limits. Existing custom `defaultMode` stays unless accepted via a one-time prompt. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 3 | 200-Subagent Cap Removed | Long-running sessions no longer refuse new subagents once they hit 200. Concurrency (default 20) and depth (5 levels) limits still apply. Removes the runaway-loop concern for long digests. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 4 | /code-review Runs as Background Subagent | `/code-review` now spawns its own context window and runs in the background; findings arrive when it completes, leaving the main conversation clean. `/review` added as alias. Effort level defaults to the last one typed. | https://code.claude.com/docs/en/whats-new/2026-w30 | ADOPT — [VERIFIED: official docs w30] | high | pending |
| 5 | Skills `context: fork` Run in Background | Skills with `context: fork` in frontmatter now run in the background by default. Add `background: false` to wait for the result in the same turn. Enables fire-and-forget skill execution with async result delivery. | https://code.claude.com/docs/en/whats-new/2026-w30 | ADOPT — [VERIFIED: official docs w30] | high | pending |
| 6 | Background Sessions: Commit/Push + Conditional PR | Background sessions that changed code in a worktree now commit and push before finishing. Draft PR is opened only when the task calls for one, and they follow git instructions in CLAUDE.md. Refines the prior "auto-PR" behavior. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 7 | 20 Concurrent Subagents Default | Sessions now run up to 20 subagents concurrently (was unspecified). Tunable via `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`. Explicit control for routines that need tighter or broader parallelism. | https://code.claude.com/docs/en/whats-new/2026-w30 | ADOPT — [VERIFIED: official docs w30] | high | pending |
| 8 | Ultraplan Removed | The `/ultraplan` command and `ultraplan` keyword are removed in v2.1.220+. Use plan mode or Claude Code on the web instead. Any saved skill or routine referencing `/ultraplan` will break silently. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |
| 9 | /fork Now Uses Its Own Worktree | Sessions copied with `/fork` now make code changes in a dedicated worktree rather than the original session's checkout. Eliminates cross-session filesystem conflicts when forking research lanes. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |
| 10 | Claude Opus 5 | New default Opus model. 1M-token context window on Anthropic API and most plans. Fast mode at $10/$50/MTok. Replaces Opus 4.8 as the default on Max, Team Premium, and Enterprise pay-as-you-go. | https://code.claude.com/docs/en/whats-new/2026-w30 | WATCH — [VERIFIED: official docs w30] | high | pending |
| 11 | Self-Hosted Environments | Run Claude Code cloud sessions on org infrastructure via `claude self-hosted-runner setup`. Sessions launched from claude.ai or apps run inside your network with access to internal services. Team and Enterprise public beta. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |
| 12 | Claude Security Plugin | Official Anthropic marketplace plugin: multi-agent vuln scan (architecture map → threat model → hunt → independent review). Scans repo, diff, PR, or commit. Writes findings to `CLAUDE-SECURITY-<timestamp>/`. Install with `/plugin install claude-security@claude-plugins-official`. | https://code.claude.com/docs/en/whats-new/2026-w30 | WATCH — [VERIFIED: official docs w30] | high | pending |
| 13 | Worktree Isolation Strengthened | Worktree isolation now blocks Bash commands and git redirects that reach the main checkout, in all session types including subagents. PreToolUse auto-allow hooks no longer bypass restrictions in internal side tasks (summaries, compaction). Security improvement. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |
| 14 | MemPalace 4-Layer Memory Taxonomy | Third-party pattern (multi-agent-ralph-loop): 4-layer memory stack (L0: identity 818 tokens, L1: actionable rules, L2: project taxonomy in halls/rooms/wings, L3: full knowledge base on-demand). Key insight: "Selection beats encoding" — fewer rules loaded outperforms compression. Extractable as a native pattern without installing third-party code. | https://github.com/alfredolopez80/multi-agent-ralph-loop | TEST — [UNVERIFIED: third-party; pattern extractable natively] | medium | pending |
| 15 | Parallel Agent Team + 4-Stage Quality Gates | Third-party pattern (multi-agent-ralph-loop): complexity-gated routing (≥3 → parallel specialist agents, <3 → direct); 4-stage blocking gates (CORRECTNESS → QUALITY → SECURITY → CONSISTENCY); enforced via TeammateIdle/TaskCompleted hooks. Extractable as a department-routing pattern for brain routines. | https://github.com/alfredolopez80/multi-agent-ralph-loop | TEST — [UNVERIFIED: third-party; patterns extractable natively] | medium | pending |

---

## Patterns Worth Knowing

### 1. Cross-Session Messaging Enables Runtime Brain Coordination

Sessions can now discover each other via `ListAgents` and pass text via `SendMessage`. For compound-brain this means: a `brain-orient` session can send a finding to a `brain-write` session without the user re-explaining context. The key constraint is that only text is passed — no history, no files — so sessions must still be self-contained enough to act on a one-paragraph message. Design skill calls with this in mind: a skill that needs to hand off to another skill should emit a compact, actionable message, not a full context dump.

### 2. Auto Mode as Default Changes the Trust Model for Autonomous Routines

Starting August 14, auto mode is the default for new sessions on Pro/Max/Team. This is architecturally significant for compound-brain: cron/scheduled sessions will now operate under the auto-mode classifier rather than the previous permission-prompt model. The classifier handles safe actions without interruption and blocks risky ones. Classifier calls don't count toward usage limits. This changes the permission-setup session recommendation from the 08-04 digest: instead of approving specific tools in `settings.local.json`, the right default posture is now auto mode + explicit deny rules for actions that should always block (existing `settings.json` deny rules already cover the critical paths).

### 3. Tiered Memory Loading: Selection Beats Encoding

The MemPalace pattern from multi-agent-ralph-loop formalizes something the brain already does informally: not all memory is loaded at session start. The key insight is that selection (loading only the right rules) outperforms compression (loading everything but shorter). The 4-layer taxonomy (L0: 818-token identity, L1: actionable rules, L2: project taxonomy, L3: full KB) maps directly onto the brain's existing structure — AGENTS.md ≈ L0+L1, knowledge/projects/ ≈ L2, knowledge/ tree ≈ L3. The implication: the brain should explicitly tag which knowledge is "must-load at session start" (L0/L1) vs "load on demand" (L2/L3) to reduce startup token cost.

### 4. The /fork Worktree Change Fixes a Prior Risk

The 08-04 digest listed `/fork for research lanes` as a brain upgrade opportunity. That recommendation assumed the forked session operated in the original checkout — which was a cross-session filesystem risk. Week 32 fixes this: `/fork` now allocates a dedicated worktree for the forked session. The upgrade opportunity is now clean to adopt without the conflict concern.

### 5. Ultraplan Removal: Stored Prompts Need a Sweep

Ultraplan (`/ultraplan`, `ultraplan` keyword) is removed in v2.1.220+. Any stored prompt, skill, or routine that referenced Ultraplan now has a dead reference. For compound-brain: review `.brain/routines/`, `.brain/knowledge/skills/`, and any queued proposals for `/ultraplan` references and replace with plan mode or Claude Code on the web equivalent.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| Cross-session messaging | brain-orient ↔ brain-write skill handoff | Pass findings between skills without user re-explaining; compact message format reduces context waste |
| MemPalace L0/L1 tagging | AGENTS.md + knowledge/_index.md | Tag must-load vs on-demand knowledge; reduces startup token cost; makes session-start more predictable |
| `context: fork` for research lanes | weekly-digest-prompt.md | Research lanes run as background skills; main session synthesizes results; already recommended in 08-04, now has native mechanism |
| Auto mode + deny rules audit | .claude/settings.json + settings.local.json | Auto mode is now default; verify deny rules cover all protected paths (hooks, scripts, CLAUDE.md, prod surfaces) before Aug 14 switch |
| Complexity routing rule | brain routine dispatch | Add explicit complexity-gating: single-department task → direct; cross-department or >3-step task → parallel agent teams |
| 4-stage quality gates | skill output validation | Add CORRECTNESS → QUALITY → SECURITY → CONSISTENCY gate sequence as a standard review pattern for any brain routine that produces artifacts |
| Claude Security plugin | code security review | Scan brain-related code changes for vulnerabilities before merging; run on `.claude/` changes |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Update Prior Digest Outcome Field — /fork Worktree Evolution

**Risk: SAFE** — markdown edit under `.brain/knowledge/research/`

The 2026-08-04 digest, item #9 "Background Agents Auto-PR," listed outcome as `pending`. Week 32 refined this behavior: background sessions now open a draft PR **only when the task calls for one** and follow CLAUDE.md git instructions. This is a behavior change from the prior description ("auto-PR on worktree completion"). Update outcome note in the prior digest to reflect the refinement.

✅ Applied — see 2026-08-04-llm-architecture-digest.md item #9 outcome field updated below.

---

### [SAFE-2] Add New Queue Items

**Risk: SAFE** — markdown append to `.brain/queue.md`

New items surfaced this run:
- 012: Audit routines and skills for `/ultraplan` references; replace with plan mode (medium, pending)
- 013: Tag L0/L1 knowledge in AGENTS.md and knowledge/_index.md for tiered loading (medium, pending)
- 014: Evaluate Claude Security plugin on `.claude/` changes (medium, pending)
- 015: Cross-session messaging prototype: brain-orient passes finding to brain-write (low, pending)

✅ Applied — see updated queue.md.

---

### [SAFE-3] Append MemPalace Pattern to Knowledge Resources

**Risk: SAFE** — markdown write under `.brain/knowledge/resources/`

Distill the extractable MemPalace pattern into `.brain/knowledge/resources/mempalace-memory-taxonomy.md` as a reference for the brain's tiered knowledge loading strategy.

✅ Applied — see file written below.

---

## Recommended Actions

1. **Before August 14: verify auto mode deny rules cover all critical paths.** Auto mode becomes the default on August 14. The classifier handles most permission prompts automatically, but explicit deny rules in `settings.json` for hooks, scripts, CLAUDE.md edits, and any production surfaces should be audited now, before the transition. This is a targeted review of `.claude/settings.json` and `.claude/settings.local.json`. Needs approval to modify settings files.

2. **Adopt `context: fork` for weekly digest research lanes.** The 4-lane scan in this routine currently runs sequentially in the main session. Adding `context: fork` to research skill calls would run lanes as background subagents — results arrive async, main session synthesizes. This is now the recommended pattern (official docs w30). Update to `weekly-digest-prompt.md` needs approval (routine touches are outside the SAFE allowlist since the file governs autonomous behavior).

3. **Audit for `/ultraplan` references.** The command and keyword are removed in v2.1.220+. Sweep `.brain/routines/`, `.brain/knowledge/skills/`, `.brain/candidate-skills/`, and any queued proposals. No `/ultraplan` references found in this repo in this run — but worth confirming with a grep before the next session.

---

## Needs Approval

- **Auto mode deny rule audit** — reviewing and potentially modifying `.claude/settings.json` and `.claude/settings.local.json` requires approval
- **Update `weekly-digest-prompt.md` to use `context: fork` for research lanes** — routine file governs autonomous behavior; edits require approval
- **Cross-session messaging prototype** — requires testing in a live session with multiple open sessions; interactive, not automatable
- **Claude Security plugin evaluation** — installing and running a plugin requires approval
- **Self-hosted environments evaluation** — Team/Enterprise feature; requires org-level admin action
- **Complexity routing and 4-stage quality gates** — any implementation in `.claude/departments/` or hooks requires approval
