# LLM Architecture Digest: 2026-11-23

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** 4-lane research scan covering official Claude Code docs weeks 31–37 (Aug 3–Sep 11, 2026),
Anthropic engineering posts (Managed Agents, Effective Harnesses), and 2026 arXiv memory papers.
Prior digests covered through week 30 and earlier. No re-reporting of prior findings.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | `claude plugin eval` | Built-in plugin testing framework: runs test cases, scores results, compares against no-plugin baseline. `claude plugin eval init` drafts test cases and graders automatically. | https://code.claude.com/docs/en/whats-new/2026-w37 | ADOPT — [VERIFIED: official docs w37] | high | pending |
| 2 | Cross-session messaging | On macOS and Linux, Claude Code sessions can message each other with `@`-mention in the prompt or via SendMessage. Enables research-lane → synthesis-session handoffs without user relay. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 3 | `/skill-doctor` | Shows each skill's context cost and usage frequency so you can turn off unused skills. Every loaded skill costs tokens on every turn. | https://code.claude.com/docs/en/whats-new/2026-w36 | ADOPT — [VERIFIED: official docs w36] | high | pending |
| 4 | Fork mode on by default | Interactive sessions now default to fork mode: Claude delegates side tasks to subagents that inherit the full conversation. Changes the orchestration baseline for all sessions. | https://code.claude.com/docs/en/whats-new/2026-w33 | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 5 | Anthropic Managed Agents: harness-as-cattle | Harness runs outside the container, calls tools through `execute(name, input)`. Session log lives outside the harness — crash recovery by resuming from the last event. Session log is an external context object; `getEvents()` slices it before Claude sees it. | https://anthropic.com/engineering/managed-agents | ADOPT — [VERIFIED: official Anthropic engineering post] | high | pending |
| 6 | Effective harnesses: two-agent split + structured feature list | Initializer agent (run once): creates environment, writes structured JSON feature list with pass/fail per feature; Coding agent (every session): reads progress, picks one feature, verifies it end-to-end. JSON over Markdown because model is less likely to overwrite it. One feature at a time is explicitly "critical." | https://anthropic.com/engineering/effective-harnesses-for-long-running-agents | ADOPT — [VERIFIED: official Anthropic engineering post] | high | pending |
| 7 | `--restricted` mode | Starts Claude without command-running tools (Bash, WebFetch); confines file tools to working dirs; loads only managed settings; refuses bypassPermissions. Use `--tools` to selectively restore tools. Designed for eval harnesses on shared machines. | https://code.claude.com/docs/en/whats-new/2026-w35 | WATCH — [VERIFIED: official docs w35] | high | pending |
| 8 | PreModelSwitch / PostModelSwitch hooks | New hook events that fire before/after a model change. PreModelSwitch can block a switch; PostModelSwitch can inject context after the new model is active. | https://code.claude.com/docs/en/whats-new/2026-w36 | WATCH — [VERIFIED: official docs w36] | high | pending |
| 9 | `promptCacheTtl` / `subagentPromptCacheTtl` settings | Set `promptCacheTtl: "1h"` for 1-hour prompt cache on the main conversation (API key or cloud provider). `subagentPromptCacheTtl` controls all subagents and other non-main requests. Direct cost lever for routines with multiple turns. | https://code.claude.com/docs/en/whats-new/2026-w35 | WATCH — [VERIFIED: official docs w35] | high | pending |
| 10 | Managed MCP servers for organizations | Organizations can list HTTP/SSE MCP servers under `managedMcpServers` in managed settings to push them to all users automatically, in addition to user-added servers. | https://code.claude.com/docs/en/whats-new/2026-w36 | WATCH — [VERIFIED: official docs w36] | medium | pending |
| 11 | Auto mode default for new sessions | Auto mode became the default permission mode for new sessions on Pro, Max, and Team plans (started Aug 14, 2026). Changes the baseline for all new compound-brain cloud sessions. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |
| 12 | EvolveMem: self-evolving memory via AutoResearch | Co-evolves stored knowledge AND retrieval settings; treats retrieval configuration as a search space that an LLM improves through AutoResearch diagnosis. 18.9% relative improvement on benchmarks; evolved configs transfer across benchmarks without catastrophic forgetting. Code at github.com/aiming-lab/SimpleMem. | https://arxiv.org/abs/2605.13941 | TEST — [UNVERIFIED: third-party research; pattern extractable, do not install] | medium | pending |
| 13 | D²ACCI: dual-loop diagnostic protocol for memory changes | Outer gate promotes/feature-flags/rejects memory interventions based on paired statistics, slice monitors, and stage traces. Applied to MemStack: 93.59% LoCoMo, 90.93% LongMemEval. 98–100% DCR@3 on diagnostic artifacts vs. 0% for results-only logs. Gives a principled audit trail for memory system changes. | https://arxiv.org/abs/2608.17756 | TEST — [UNVERIFIED: third-party research; protocol extractable, do not install] | medium | pending |
| 14 | MemChain: structured retrieval traces for LLM agents | Post-retrieval policy: drafts a question-specific evidence plan, builds an ordered evidence trace, runs explicit memory actions to produce context. Trained with supervised trace learning then TMPO (RL). State-of-the-art on LoCoMo and LongMemEval-S while shrinking context. Code at github.com/mayiwen0212/MemChain. | https://arxiv.org/abs/2607.24097 | TEST — [UNVERIFIED: third-party research; pattern extractable, do not install] | medium | pending |
| 15 | Mem²Evolve: co-evolutionary capability expansion (ACL 2026) | Pairs Asset Memory (created artifacts, tools) with Experience Memory (task outcomes). Agent dynamically creates new assets to expand its capability boundary during task execution. Accepted to ACL 2026. | https://arxiv.org/abs/2604.10923 | WATCH — [UNVERIFIED: third-party research; pattern extractable] | medium | pending |

---

## Patterns Worth Knowing

### 1. Harness-as-Cattle: Session Log as the Source of Truth

Anthropic's Managed Agents post makes this architecture explicit: the session log lives outside the harness, so the harness is stateless and replaceable. If a harness crashes, a new one resumes from the last log event. For compound-brain, this maps directly to the `--resume` / `.brain/state/` pattern — the state files are the session log. The implication: any crash-recovery or cross-session handoff should read from `.brain/state/`, not from in-memory context.

### 2. Two-Agent Split for Long-Running Loops

The "Effective Harnesses" post gives a concrete pattern: one initializer agent that runs once (sets up environment, writes a JSON progress file with pass/fail per task), and one coding agent that runs every session (reads progress, picks one task, verifies end-to-end, commits, marks done). The key insight is JSON over Markdown for the feature list (model less likely to overwrite), and "one task per session" as a hard architectural constraint. This is the right model for compound-brain's autoresearch protocol — right now the weekly digest does too much in one context window.

### 3. `claude plugin eval` Closes the Verification Loop for Brain Skills

The plugin eval command runs test cases against a plugin with and without it active, scoring what the plugin contributes. `claude plugin eval init` drafts the cases. This directly closes queue item 009 (verify the plugin loads and works in a cloud session). The eval approach is safer than a live session test: it's reproducible, leaves a scored report, and doesn't affect real brain state.

### 4. Memory Self-Evolution: AutoResearch Over Retrieval Configuration

EvolveMem (arXiv 2605.13941) treats retrieval settings (not just stored content) as a search space to optimize. The AutoResearch loop uses diagnosis (what retrieval patterns fail?) to propose config changes, tests them, and promotes the best. For compound-brain, this suggests the SAGE novelty gate (queue 005) is only half the picture — the retrieval side also needs periodic re-calibration, not just the write side. The practical move: add a `retrieval-config.md` to `.brain/knowledge/resources/` that tracks current retrieval heuristics and flags when they should be re-evaluated.

### 5. Diagnostic Traces as the Audit Contract for Memory Changes

D²ACCI (arXiv 2608.17756) formalizes something compound-brain currently does informally: the weekly digest is an outer gate that decides whether a memory change should be promoted. The D²ACCI protocol adds paired statistical comparison (not just outcome), slice-level non-regression (do protected categories get worse?), and stage-level diagnostic traces (what exactly happened at each step?). The key observation: "results-only logs" have 0% DCR@3 — meaning you can't diagnose failures from outcome metrics alone. The weekly AGENTS.md learnings are currently results-only. Adding a brief "what failed / what was inconclusive" trace would make them far more useful.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| `claude plugin eval` | compound-brain plugin verification | Closes queue 009 reproducibly; leaves scored report; safer than live test |
| Cross-session messaging | Weekly digest research lanes | Fork 4 research lanes, each sends findings to synthesis session; replaces sequential scan |
| `/skill-doctor` report | Plugin skill management | Identify loaded skills that are never triggered; prune context overhead |
| Two-agent split (initializer + coding) | Autoresearch protocol spec | Weekly digest moves to: initializer (one-time env setup + JSON task list) + coding agent (one task per session) |
| Harness-as-cattle / session log outside harness | `.brain/state/` design | Explicitly document that `.brain/state/` is the external context object; harness (the weekly routine) is stateless |
| PreModelSwitch / PostModelSwitch hooks | Session governance | Block model switches that would change autonomy depth mid-session; log all model changes to brain |
| `promptCacheTtl: "1h"` | Weekly digest routine cost | Multi-turn research sessions now cache the main conversation for 1 hour; reduces cost for iterative research |
| EvolveMem AutoResearch pattern | `.brain/knowledge/resources/` | Add `retrieval-config.md` tracking current retrieval heuristics and when to re-evaluate them |
| D²ACCI diagnostic traces | AGENTS.md learnings format | Add "what failed / inconclusive" section to each weekly learnings entry; shift from results-only to diagnostic-trace format |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Add retrieval-config spec stub to resources

**Risk: SAFE** — markdown create under `.brain/knowledge/resources/`

Create `.brain/knowledge/resources/retrieval-config.md` documenting current retrieval heuristics used in the weekly digest (recency-first, dedup by prior-digest check, search-term diversity across 4 lanes). Note that this should be re-evaluated after any significant change to the memory architecture.

### [SAFE-2] Update prior digest outcome fields

**Risk: SAFE** — markdown edits under `.brain/knowledge/research/`

Items from 2026-08-04 digest that are now confirmed:
- Find 2 (Stacked Skill Invocations): w27 — still ADOPT pending; no implementation confirmed this run
- Find 6 (Anti-Fabrication): already marked confirmed; no change needed
- Find 1 (/doctor): run from w28; still pending human action
No changes needed to outcome fields this run — no prior ADOPT items have been implemented or invalidated by this run's findings.

### [SAFE-3] Add queue items for new actionable work

**Risk: SAFE** — markdown append to `.brain/queue.md`

New items to add:
- 012: Run `claude plugin eval` on compound-brain plugin to close queue 009 (NEEDS APPROVAL — touches plugin files)
- 013: Audit hooks for PreModelSwitch/PostModelSwitch opportunities (NEEDS APPROVAL — touches .claude/hooks/)
- 014: Set `promptCacheTtl: "1h"` in settings for cost reduction (NEEDS APPROVAL — touches settings)
- 015: Draft EvolveMem-pattern retrieval-config.md spec (SAFE)
- 016: Upgrade AGENTS.md learnings format to include diagnostic-trace section per D²ACCI pattern (SAFE)

### [SAFE-4] Draft retrieval-config.md (implements SAFE-1)

Applied in this run — see file at `.brain/knowledge/resources/retrieval-config.md` after this commit.

---

## Recommended Actions

1. **Run `claude plugin eval` on the compound-brain plugin (queue 012 / addresses queue 009).** The `claude plugin eval init` command will draft test cases for verifying the plugin loads and behaves correctly in a cloud session. This is the safest way to close queue 009 — reproducible, scored, no side effects on real brain state. Requires approval since it touches plugin files.

2. **Apply the two-agent split to the weekly digest routine.** The current routine does too much in one context window. Split into: (a) an initializer that creates/updates a JSON task list in `.brain/state/digest-tasks.json` on first run; (b) a coding agent (this routine) that picks one task, executes it, and marks it done. The JSON list tracks which research lanes have been run, preventing the routine from needing to hold all findings in context. This is a CLAUDE.md / routine change — NEEDS APPROVAL.

3. **Run `/skill-doctor` in a compound-brain cloud session.** The report shows which loaded skills are never triggered and their token cost per turn. This is a read-only audit. If unused skills are found, pruning them reduces overhead on every turn. The pruning step (turning skills off) NEEDS APPROVAL.

---

## Needs Approval

- **Queue 012: Run `claude plugin eval` on compound-brain plugin** — touches plugin files in `plugins/`; requires human review of generated test cases before first run
- **Queue 013: Add PreModelSwitch/PostModelSwitch hooks** — touches `.claude/hooks/`
- **Queue 014: Set `promptCacheTtl: "1h"` in session settings** — touches `.claude/settings.json`
- **Two-agent split refactor of weekly routine** — edits `CLAUDE.md` or `.brain/routines/`; content changes to routines require approval
- **Self-hosted environments evaluation** — infra decision; requires owner action
- **Cross-session messaging setup for research lanes** — requires a session that approves the `@`-mention / SendMessage tool; the tool is available in cloud sessions per official docs but the initial approval is attendant
- **Queue 006: Delete branch `claude/cool-heisenberg-2iokix`** — still pending; outward-facing git action on a public repo
- **Queue 007: Repo visibility public → private** — still pending; owner decision
