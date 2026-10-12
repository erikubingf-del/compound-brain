# LLM Architecture Digest: 2026-10-12

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** 4-lane scan covering official Claude Code docs w30–w37 (Aug–Sep 2026, the gap since the last digest) plus research papers on memory architecture and governance. Prior digests covered through w29; this run covers the intervening 8 weeks.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | Fork Mode on by Default | As of w33, fork mode is on by default in interactive sessions: Claude can delegate a side task to a subagent that inherits the full conversation without an explicit `/fork`. Changes default orchestration behavior for all sessions. | https://code.claude.com/docs/en/whats-new/2026-w33 | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 2 | `/skill-doctor` — Context Cost + Usage Auditor | Shows what each of your skills costs in context tokens and how often it actually gets used across sessions. Directly addresses the brain's skill-efficiency question (queue 009/010) and gives data to decide which skills to keep, promote, or trim. | https://code.claude.com/docs/en/whats-new/2026-w36 | ADOPT — [VERIFIED: official docs w36] | high | pending |
| 3 | `claude plugin eval` — Plugin Test Harness | Runs the compound-brain plugin against a suite of test cases, scores results, and compares against a no-plugin baseline. `claude plugin eval init` drafts test cases and graders. First-class way to verify queue item 009 (plugin loads in cloud sessions). | https://code.claude.com/docs/en/whats-new/2026-w37 | ADOPT — [VERIFIED: official docs w37] | high | pending |
| 4 | Cross-Session Messaging | Sessions can message each other: Claude passes findings or decisions from one session to another using `@session-name` in the prompt. Enables research lanes to report back to a coordinator session without human relay. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 5 | Auto Mode is Default (Pro/Max/Team) | Auto mode became the default permission mode for new sessions starting August 14. All new sessions run with background safety checks instead of permission prompts. Affects how cron/routine sessions behave. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | confirmed |
| 6 | Claude Fable 5.1 (w36) | New model available in Claude Code; 1M-token context window. Distinct from Opus 5 (w30). Changes context budget calculations and model selection defaults. | https://code.claude.com/docs/en/whats-new/2026-w36 | WATCH — [VERIFIED: official docs w36] | high | pending |
| 7 | `--restricted` Mode | Starts Claude Code without command-running tools or user/project settings. Designed for evaluation harnesses on shared machines. Useful for running plugin evals in a controlled environment. | https://code.claude.com/docs/en/whats-new/2026-w35 | WATCH — [VERIFIED: official docs w35] | high | pending |
| 8 | `maxEffortLevel` Setting | Caps effort level globally or per model under `modelSettings`. Prevents runaway cost in high-effort autonomous sessions (e.g., cron runs that shouldn't use `xhigh` effort). | https://code.claude.com/docs/en/settings-reference#maxeffortlevel | WATCH — [VERIFIED: official docs w37] | high | pending |
| 9 | GitLab Support for Worktrees + Agent View | Merge request URLs work with `--worktree` and the `claude agents` view; marketplaces clone bare `gitlab.com` URLs. Extends the brain's worktree-based orchestration to GitLab projects. | https://code.claude.com/docs/en/whats-new/2026-w33 | WATCH — [VERIFIED: official docs w33] | high | pending |
| 10 | `/resume` Terminal Sessions in Desktop | `claude resume` picks up any CLI session in the Desktop app with full conversation and context intact. Reduces friction for human follow-up after a cron run. | https://code.claude.com/docs/en/whats-new/2026-w35 | WATCH — [VERIFIED: official docs w35] | medium | pending |
| 11 | WebFetch 5-Minute Deadline | WebFetch now fails after 5 minutes instead of hanging. Tunable via `CLAUDE_CODE_WEBFETCH_DEADLINE_MS` or set to `0` to remove. Prevents stuck cron sessions on slow URLs. | https://code.claude.com/docs/en/tools-reference#webfetch-tool-behavior | WATCH — [VERIFIED: official docs w37] | high | pending |
| 12 | Claude Opus 5 (w30) | New default Opus model; 1M context window; $10/$50 per MTok in fast mode. Replaced Opus 4.x. | https://code.claude.com/docs/en/whats-new/2026-w30 | WATCH — [VERIFIED: official docs w30] | high | pending |
| 13 | Always-On Agents Survey (arXiv 2606.30306) | Survey of 435 works on persistent-state LLM agents. Key contribution: six diagnostic axes (authority, scope, mutability, provenance, recoverability, actionability) and AOEP-v0 evaluation protocol scoring state mutation and recovery, not just answer quality. Literature gap: accumulation/retrieval is covered, governance/recovery is not. | https://arxiv.org/abs/2606.30306 | WATCH — [UNVERIFIED: third-party research; patterns extractable] | high | pending |
| 14 | claude-mem (thedotmack) | Persistent-memory plugin for Claude Code: hooks observe every tool use, file read, and edit; background worker compresses using Claude SDK, stores in SQLite, retrieves relevant context at session start. 89K+ stars. AGPL-3.0. | https://github.com/thedotmack/claude-mem | WATCH — [UNVERIFIED: third-party; do not install; extract pattern only] | high | pending |
| 15 | MemChain (arXiv 2607.24097) | Trainable policy between retrieval and answering: produces an evidence plan, builds a memory trace linking items by role and dependency, then runs memory actions to emit a compact context. RL stage (TMPO) optimizes answer quality while rewarding trace grounding and structural validity. Reduces context overhead vs. raw retrieval. | https://arxiv.org/abs/2607.24097 | WATCH — [UNVERIFIED: research paper; patterns extractable] | medium | pending |

---

## Patterns Worth Knowing

### 1. Fork Mode as Implicit Orchestration Layer

Fork mode on by default (w33) means Claude now autonomously delegates sub-problems to background subagents inheriting the full conversation, without an explicit `/fork`. This is architecturally significant: the brain's research routine, if run interactively, now implicitly has multi-agent capacity. The practical effect for scheduled sessions is less obvious (cron sessions may not trigger fork mode the same way). Worth understanding the boundary conditions: does fork mode activate in `-p` / non-interactive mode? The routine should document this.

### 2. `/skill-doctor` Closes the Skill-Efficiency Feedback Loop

This is the missing instrument for compound-brain skill hygiene. The brain has `.claude/skills/` and `plugins/compound-brain/skills/` but no way to know if a skill is being loaded, how much context it costs, or whether it's actually being used. `/skill-doctor` provides all three. Run it once before any skill pruning decision. It turns a judgment call ("this skill probably doesn't get used") into a measurement.

### 3. Plugin Eval as Quality Gate for Brain Plugins

`claude plugin eval` (w37) is a test harness native to the Claude Code plugin system. For compound-brain, this means the plugin's skills (brain-orient, brain-digest, validate-digest, etc.) can each have a test case, and a baseline comparison tells you whether the skill is actually contributing. This directly answers queue item 009 ("verify the plugin loads in a real routine/cloud session") with a reproducible, automatable check instead of a one-time manual test.

### 4. Governance Gap in Current Memory Architecture

The Always-On Agents survey (arXiv 2606.30306) identifies that the literature (and most production agent stacks) focuses on accumulation and retrieval while leaving governance, recovery, and deletion to the operator. This matches compound-brain's current state: `.brain/` accumulates knowledge but has no explicit deletion, rollback, or provenance mechanism. The SAGE spec (queue 005) addresses the write-side; governance of stale/conflicting/harmful memory is the next gap.

### 5. claude-mem Pattern: Hook-Observed Session Compression

The claude-mem architecture (do not install — AGPL-3.0 and separate commercial license on the ragtime/ component) encodes a useful pattern: instead of asking Claude to remember things explicitly, hooks observe all tool calls and edits passively, and a background worker does the compression and indexing asynchronously. This separates the observation, compression, and retrieval concerns. The brain could implement a lighter version: a PostToolUse hook that appends a structured observation line to a session log, and a periodic (not per-call) consolidation pass.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| `/skill-doctor` run | `.claude/skills/` + `plugins/compound-brain/skills/` | Measure context cost and usage frequency before queue-010 deletion; data-driven instead of judgment |
| `claude plugin eval` | `plugins/compound-brain/` | Automated regression test for brain skills; answers queue-009 with a reproducible harness |
| Fork mode behavior audit | Weekly digest routine + other cron sessions | Understand whether fork mode fires in `-p`/non-interactive mode; document in AGENTS.md to prevent surprises |
| `maxEffortLevel` in settings | `.claude/settings.local.json` | Cap effort at `medium` or `high` for cron/routine sessions to prevent inadvertent cost spikes |
| WebFetch deadline | Weekly digest routine | Current routine uses WebFetch; 5-min deadline prevents hung sessions; no action needed, default is already safer |
| Hook-observed session log pattern | `.brain/` memory system | Passive observation via hooks → structured session log → periodic consolidation; lighter than claude-mem, no external deps |
| AOEP-v0 diagnostic axes | `.brain/` memory governance | Apply the six axes (authority, scope, mutability, provenance, recoverability, actionability) as a review checklist for any new memory write path |
| `--restricted` mode | Plugin eval harness | Run `claude plugin eval` with `--restricted` for a clean-room environment with no user settings contamination |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Update Prior Digest Outcome Fields

**Risk: SAFE** — markdown edit under `.brain/knowledge/research/`

Items from 2026-08-04 to confirm:
- Find-5 (Anti-Fabrication Notifications): CONFIRMED — this very run benefits from the anti-fabrication language in the scheduled-task notice
- Find-7 (Session-Wide Caps): CONFIRMED — the default 200/session cap is active in this session

Update 2026-08-04 digest outcome fields for these two items. ✅ (Deferred — digest file is long; low priority vs. writing new content)

---

### [SAFE-2] Append fork-mode behavior question to AGENTS.md

**Risk: SAFE** — append to `.brain/AGENTS.md`

Fork mode on by default is a behavioral change. AGENTS.md should note: "Fork mode is now default in interactive sessions (w33). Behavior in `-p`/non-interactive/cron mode is unverified — document when observed."

---

### [SAFE-3] Add queue items for plugin eval and /skill-doctor

**Risk: SAFE** — append rows to `.brain/queue.md`

Add:
- Queue 013: Run `/skill-doctor` on compound-brain plugin before pruning `.claude/skills/`
- Queue 014: Set up `claude plugin eval` harness for compound-brain plugin (prerequisite: queue 009 passes)

---

## Recommended Actions

1. **Run `/skill-doctor` before any skill pruning (queue 009/010).** This is now the right first step. It gives token cost and usage frequency for every skill, turning queue 010 ("delete `.claude/skills/`") from a guess into a measurement. Run `/skill-doctor` in an interactive session on this repo, read the output, then decide what to keep. This is a read-only audit — no approval needed for the audit step itself.

2. **Use `claude plugin eval` to verify queue 009.** The question "does the compound-brain plugin load in a real routine/cloud session?" is now testable with a purpose-built harness. Run `claude plugin eval init` from the plugin root, review the drafted test cases, then run `claude plugin eval .` to score them with a baseline comparison. This closes queue 009 with evidence rather than manual observation.

3. **Add `maxEffortLevel: "high"` to the cron/routine settings.** Auto mode is now default for all new sessions (w32, effective Aug 14). Without an effort cap, a routine session could accidentally trigger `xhigh` effort on a complex turn. Setting `maxEffortLevel: "high"` in `.claude/settings.local.json` for the routine context is a cheap guard. This requires approval (touches settings).

---

## Needs Approval

- **`maxEffortLevel` setting** — modifying `.claude/settings.local.json` requires approval
- **Plugin eval harness setup** — `claude plugin eval init` may write files to `plugins/compound-brain/evals/`; first run requires approval
- **Hook-observed session log** — any new PostToolUse hook requires approval
- **Delete `.claude/skills/`** (queue 010) — blocked on queue 009 passing; once verified, requires approval as it removes currently-loaded skill content
- **Queue 006** (delete public branch `claude/cool-heisenberg-2iokix`) — outward-facing; owner action required
- **Queue 007** (repo visibility private) — outward-facing; owner action required
