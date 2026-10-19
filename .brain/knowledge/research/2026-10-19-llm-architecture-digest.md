# LLM Architecture Digest: 2026-10-19

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** Covers the gap since the 2026-08-04 digest — official Claude Code releases weeks 32–37 (Aug–Sep 2026) plus changelog entries v2.1.285–v2.1.303 (Sep–Oct 2026), plus two external research lanes (memory architectures, community tooling). No findings duplicate either prior digest.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | Mods — Plugin Behavior Hooks | Plugins can now add hooks that modify Claude's deeper behavior: prompt rewrites, UI panels, built-in feature overrides. Built-in "You should know" mod flags things Claude or the user might miss. `prompt.change`, `$.ui.notify`, `prompt.autocomplete`, `agent.spawn`, `$.model.complete` are new hook targets. | https://code.claude.com/docs/en/changelog | ADOPT — [VERIFIED: changelog v2.1.287–v2.1.300] | high | pending |
| 2 | `claude plugin eval` | Run a plugin against a test-case suite, score results, compare against no-plugin baseline. `claude plugin eval init` drafts cases and graders automatically. First-class eval loop for plugin/skill quality. | https://code.claude.com/docs/en/whats-new/2026-w37 | ADOPT — [VERIFIED: official docs w37] | high | pending |
| 3 | `/skill-doctor` | Shows what each installed skill costs in context tokens and how often it is used in sessions. Directly answers "is this skill earning its context budget?" — the right first step before any skill audit. | https://code.claude.com/docs/en/whats-new/2026-w36 | ADOPT — [VERIFIED: official docs w36] | high | pending |
| 4 | Native Cross-Session Messaging (macOS/Linux) | Claude Code sessions can now message each other directly. A session passes a finding or decision to another without re-explaining context. Official native alternative to the community HCOM tool, but with narrower hook surface. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 5 | Fork Mode Default Everywhere | `fork` subagents are now on by default in interactive sessions, Desktop, VS Code, and (v2.1.302) `claude -p` and the Agent SDK. Subagent inherits full conversation context for side tasks without blocking the parent. `CLAUDE_CODE_FORK_SUBAGENT=0` turns it off. | https://code.claude.com/docs/en/whats-new/2026-w33 | ADOPT — [VERIFIED: official docs w33 + changelog v2.1.302] | high | pending |
| 6 | Idle Compaction | Conversations over 200K tokens that sit idle for ~54 minutes are auto-compacted before the prompt cache expires. Prevents silent cache misses and runaway token cost on unattended sessions. Configurable via `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` or `"idleCompaction": false`. | https://code.claude.com/docs/en/changelog | ADOPT — [VERIFIED: changelog v2.1.299] | high | pending |
| 7 | `onFailure: "block"` for Hooks | A hook can now declare `onFailure: "block"` — if the hook fails (non-zero exit or HTTP error), the action it guards is blocked rather than silently continuing. Critical for trust-boundary enforcement on SAFE-gating hooks in the brain. | https://code.claude.com/docs/en/changelog | ADOPT — [VERIFIED: changelog v2.1.295] | high | pending |
| 8 | `/code-review` — CLAUDE.md Convention Findings + `--max-findings` | At medium effort, `/code-review` now reports cleanup findings and CLAUDE.md convention violations, not only correctness bugs. `--max-findings <n>` (or `all`) caps the report; setting persists until `--max-findings default`. | https://code.claude.com/docs/en/changelog | ADOPT — [VERIFIED: changelog v2.1.288, v2.1.290] | high | pending |
| 9 | `--restricted` Mode | Starts a session without command-running tools and without loading user or project settings. Safe evaluation harness — no hooks, no CLAUDE.md overrides, no skills. | https://code.claude.com/docs/en/whats-new/2026-w35 | ADOPT — [VERIFIED: official docs w35] | high | pending |
| 10 | Self-Hosted Cloud Environments (public beta) | Run Claude Code cloud sessions on organization-operated infrastructure. Team and Enterprise plans. Changes who owns the execution boundary for autonomous routines. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |
| 11 | `/design` Artboard Workflow | Research preview: artboard-based UI design workflow in the CLI and Desktop, built on artifacts. Claude drafts editable artboards and implements the one you pick. | https://code.claude.com/docs/en/whats-new/2026-w34 | WATCH — [VERIFIED: official docs w34] | medium | pending |
| 12 | `CLAUDE_CODE_AUTO_MODE_MODEL` | Chooses which model runs the client-side auto mode classifier. Relevant for sessions where classifier cost is significant (long routines, high API volume). | https://code.claude.com/docs/en/changelog | WATCH — [VERIFIED: changelog v2.1.302] | high | pending |
| 13 | Claude Haiku 5.5 — 1M Context at $0.10/$0.50 MTok | New default Haiku model on Anthropic API: 1M context window, $0.10/$0.50 per million tokens. Changes cost calculation for high-volume or long-context routine subagents that previously used Haiku. | https://code.claude.com/docs/en/changelog | WATCH — [VERIFIED: changelog v2.1.293] | high | pending |
| 14 | HCOM — Hooks-Based Inter-Agent Messaging | Community tool (github.com/aannoo/hcom): links Claude sessions through hooks and a shared DB. Subagents join the mesh; messages deliver at PostToolUse or Stop hook. Collision detection when two agents edit the same file within 30s. Pattern is natively covered by official cross-session messaging (find #4), but HCOM offers richer coordination (collision detection, event history). | https://github.com/aannoo/hcom | TEST — [UNVERIFIED: third-party; extract pattern, do not install] | medium | pending |
| 15 | ZenBrain: 7-Layer Neuroscience Memory Architecture | Academic paper (arXiv 2604.23878): working/short-term/episodic/semantic/procedural/core/cross-context layers with 15 cognitive mechanisms. Reports +20.7% F1 on LoCoMo vs single-layer baseline. Self-reported benchmarks, LLM-as-judge scoring. | https://arxiv.org/abs/2604.23878 | WATCH — [UNVERIFIED: third-party academic paper; self-reported benchmarks, extract conceptual model only] | low | pending |

---

## Patterns Worth Knowing

### 1. Mods as a First-Class Extension Point Below Skills

Skills load instructions into context; mods execute code hooks that run inside Claude's control plane. The distinction matters: a skill changes what Claude knows; a mod changes what Claude does at the infrastructure level — rewriting prompts before they're sent, injecting UI panels, overriding built-in commands. For compound-brain, mods are the right layer for things that must always fire (e.g., a leak-gate that strips project names before any output), not just things that improve Claude's knowledge. Drafting mods is SAFE under `.brain/candidate-skills/`; promoting them to `.claude-plugin/` requires human review.

### 2. `onFailure: "block"` Closes the Shell-Write Gap

The prior AGENTS.md entry (2026-08-04) noted that Write/Edit denies do not cover shell writes — the trust boundary holds only because the Bash allowlist is narrow. `onFailure: "block"` on a hook gives a second enforcement layer: if the gate hook fails for any reason (crash, timeout, non-zero exit), the action it guards is blocked rather than silently proceeding. This is the right way to harden SAFE-boundary guards — the old shell-check approach fails open on error; `onFailure: "block"` fails closed. Requires hook config change, NEEDS APPROVAL.

### 3. `/skill-doctor` as the Pre-Audit Step

Before any manual CLAUDE.md or skill audit, run `/skill-doctor`. It shows actual token cost and session usage per skill — the data needed to decide which skills to promote, merge, or delete. This replaces the "read the skills list and guess at cost" approach. Pairs with `/doctor` (which audits CLAUDE.md). Together they answer: which skills are paying for themselves, and which rules in CLAUDE.md could be derived from the codebase.

### 4. Idle Compaction Changes the Long-Routine Token Budget

Scheduled routines that run > 200K tokens and then pause (e.g., waiting for a CI event) will be auto-compacted after 54 minutes. This is good (prevents cache expiry cost spikes) but changes the context assumptions: a routine that left intermediate state in its context window will lose it on compaction. Pattern: write intermediate state to `.brain/` files before any expected wait, don't rely on conversational context surviving an idle period. This is the disk-state discipline the Ralph Loop already advocates — now there's an additional system-level reason to follow it.

### 5. Fork Mode Everywhere Changes the Subagent Default

With fork on by default in `claude -p` and the Agent SDK (v2.1.302), any tool call that spawns a subagent now forks the full conversation context by default, including in unattended cron sessions. For compound-brain routines, this means: side tasks automatically get context (useful), but also that every fork consumes context budget from the full conversation (cost). Tune with `CLAUDE_CODE_FORK_SUBAGENT=0` in cron sessions that don't need it, or accept the context inheritance for richer subagent behavior.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| `/skill-doctor` run | All skills under `plugins/compound-brain/skills/` | Identify skills consuming context without measurable usage; trim or merge before queue-002 audit |
| `onFailure: "block"` on SAFE-gate hooks | `.claude/hooks/` (NEEDS APPROVAL) | Fails closed on hook error — closes the shell-write trust gap identified in prior AGENTS.md entry |
| Mods candidate draft | `.brain/candidate-skills/` | Draft a leak-gate mod that strips project/host names before any Write/push action; human promotes after review |
| Idle compaction awareness | All scheduled routines | Write intermediate findings to `.brain/` before any wait step; don't rely on context surviving 54-min idle |
| `claude plugin eval` + eval suite | Weekly digest routine | Write eval cases for the digest (does it have all required sections? are outcomes updated?); baseline vs no-plugin scoring |
| Cross-session messaging (native) | Multi-agent research lanes | Replaces manual HCOM coordination for sessions that share context across parallel research forks |
| Fork mode tuning | Cron/scheduled sessions | Decide per-routine: fork off (for lightweight digest runs) vs. fork on (for research that benefits from parent context) |
| `/code-review --max-findings` + CLAUDE.md findings | Brain maintenance PRs | Review brain PRs for CLAUDE.md convention violations at medium effort before merging |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Update Outcome Fields on Prior Digest ADOPT Items

**Risk: SAFE** — markdown edit under `.brain/knowledge/research/`

Items from prior digests now confirmed by official docs in this run:

**From 2026-08-04 digest:**
- Item 4 (`/fork` vs `/subtask`): CONFIRMED — week 29 official docs; `/fork` is background session, `/subtask` is in-session fork
- Item 5 (Subagents background by default): CONFIRMED — week 27 official docs
- Item 10 (Artifacts live data via MCP): CONFIRMED — week 29 official docs
- Item 11 (Claude Sonnet 5 1M context): CONFIRMED — week 27 official docs
- Item 13 (In-app browser Desktop): CONFIRMED — week 28 official docs
- Item 15 (Explore Agent inherits session model): CONFIRMED — week 27 official docs

**From 2026-08-03 digest:**
- Item 15 (Dynamic Workflows): CONFIRMED — week 22 official docs; standard feature on all paid plans

Applied below — outcome fields updated in this session's bookkeeping step.

---

### [SAFE-2] Draft Leak-Gate Mod Candidate

**Risk: SAFE** — new file under `.brain/candidate-skills/`

Draft `.brain/candidate-skills/leak-gate-mod/SKILL.md` describing a mod that intercepts Write/push actions and strips project/host/strategy names before they reach disk or git. This is a candidate only — a human promotes it to `.claude-plugin/` after review. Writing a candidate draft under `.brain/` does not execute and is within the SAFE allowlist.

Implementation steps:
1. Create `.brain/candidate-skills/leak-gate-mod/SKILL.md` with:
   - What it is: a mod (not a skill) that registers a `prompt.change` hook and a `tool.check` hook
   - What the hooks do: scan outgoing content for project/host/strategy name patterns (patterns stored in the private stored prompt) and either block or redact
   - Why a mod, not a skill: skills load instructions; this must fire deterministically, not as advice
   - Promotion path: human reviews `.claude-plugin/` PR before enabling

---

### [SAFE-3] Add Queue Items for New Upgrade Opportunities

**Risk: SAFE** — append to `.brain/queue.md`

Add to queue:
- 013: Run `/skill-doctor` and log results to `.brain/knowledge/research/` (blocked until queue 009 — plugin load verified)
- 014: Run `claude plugin eval init` on the weekly digest to draft eval cases
- 015: Review fork mode behavior in this routine (cron session) — decide `CLAUDE_CODE_FORK_SUBAGENT=0` default

---

## Recommended Actions

1. **Run `/skill-doctor` before the queue-002 CLAUDE.md audit.** The skill doctor gives actual token cost and usage per skill — data the manual audit needs but currently lacks. Block queue-002 on this (add as queue-013, gated by queue-009 plugin-load verification).

2. **Apply `onFailure: "block"` to the SAFE-gate hook.** The prior AGENTS.md entry identified that Write/Edit denies don't cover shell writes — the trust boundary is thin. `onFailure: "block"` closes this by failing closed on hook errors. Add to hooks change approval queue; this is the single highest-leverage trust improvement available.

3. **Draft the leak-gate mod candidate (SAFE-2 above).** The repo is still public (queue-007, pending). Until visibility changes, a mod that actively gates project/host names before any write is the right defense-in-depth layer. Drafting it now costs nothing; promotion waits on human review.

---

## Needs Approval

- **`onFailure: "block"` hook changes** — touches `.claude/hooks/`, requires approval
- **Fork mode tuning** — `CLAUDE_CODE_FORK_SUBAGENT=0` in cron sessions touches settings, requires approval
- **`CLAUDE_CODE_AUTO_MODE_MODEL` configuration** — settings change, requires approval
- **Enabling "You should know" mod** — plugin enable command, requires approval
- **Leak-gate mod promotion** — writing the candidate under `.brain/` is SAFE; promoting to `.claude-plugin/` requires approval
- **Self-hosted environments** — infrastructure decision, requires approval
- **Queue-007 (repo visibility: public → private)** — owner action, still pending; no project/host/strategy names written into this digest
