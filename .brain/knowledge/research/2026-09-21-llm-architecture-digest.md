# LLM Architecture Digest: 2026-09-21

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** Weeks 32–37 (2026-08-03 through 2026-09-11). Prior digests covered through W29.
Four lanes: GitHub trending LLM/agents, Claude Code ecosystem, community/research techniques, official docs.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | `claude plugin eval` | First-party plugin/skill eval runner. Runs test cases, scores with graders, compares against a no-plugin baseline, produces HTML+JSON reports. `init` subcommand drafts test suite interactively. `tool_used: Skill` grader specifically checks skill routing. | https://code.claude.com/docs/en/plugin-evals | ADOPT — [VERIFIED: official docs w37] | high | pending |
| 2 | `/skill-doctor` context cost and usage tracking | Shows context token cost and invocation frequency per skill. Every enabled skill adds context overhead on every turn even if never invoked. Identifies unused skills to trim. | https://code.claude.com/docs/en/skills#find-unused-skills | ADOPT — [VERIFIED: official docs w36] | high | pending |
| 3 | `--restricted` mode for eval harnesses | Starts Claude Code without command-running tools, WebFetch, and restricts file tools to working dir. Designed for eval harnesses on shared machines. Also removes bypassPermissions mode. Use `--tools` to restore specific tools selectively. | https://code.claude.com/docs/en/cli-reference#cli-flags | ADOPT — [VERIFIED: official docs w35] | high | pending |
| 4 | `promptCacheTtl` setting for autonomous sessions | Set to `1h` for a one-hour prompt cache on the main conversation when using an API key or cloud provider. `subagentPromptCacheTtl` sets it for subagents. Directly reduces cold-start cost for scheduled/cron sessions. | https://code.claude.com/docs/en/prompt-caching#choose-the-ttl-yourself | ADOPT — [VERIFIED: official docs w35] | high | pending |
| 5 | Fork mode on by default; `@` session messaging | Fork mode default in interactive sessions: Claude can spawn a fork subagent that inherits the full conversation + prompt cache. Type `@name` in prompt to message another live session directly via `SendMessage`. Unique session names enforced. | https://code.claude.com/docs/en/sub-agents#turn-fork-mode-on-or-off | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 6 | Task tools disabled on newer models | `TaskCreate`, `TaskUpdate`, `TodoWrite` (and related) are no longer available on Sonnet 5, Fable 5, Mythos 5, and later model families. Set `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` to re-enable. | https://code.claude.com/docs/en/tools-reference#task-tool-availability | ADOPT (awareness) — [VERIFIED: official docs w33] | high | pending |
| 7 | `defaultMode: bypassPermissions` blocked in project settings | Setting `defaultMode: "bypassPermissions"` in a project's `.claude/settings.json` or `.claude/settings.local.json` no longer takes effect; session starts in Manual mode. Must be in user or managed settings, or pass `--permission-mode`. | https://code.claude.com/docs/en/permission-modes#which-mode-a-session-starts-in | ADOPT (security hardening) — [VERIFIED: official docs w36] | high | pending |
| 8 | Cross-session messaging via `@` and `SendMessage` | On macOS/Linux, Claude Code sessions on the same machine can message each other. Type `@` in prompt to mention a session by name. Claude uses `SendMessage` tool directly. Bare name that matches exactly one live session delivers without confirmation. Also now available on Bedrock, GCP Agent Platform, and Microsoft Foundry. | https://code.claude.com/docs/en/cross-session-messaging | WATCH — [VERIFIED: official docs w32/w33] | high | pending |
| 9 | Subagent `maxTurns` returns partial output with `SendMessage` hint | A subagent that stops at its `maxTurns` limit now returns output marked as partial with a hint that Claude can continue it with `SendMessage`, instead of appearing to have finished. Enables multi-step orchestration with turn budget. | https://code.claude.com/docs/en/sub-agents#resume-subagents | WATCH — [VERIFIED: official docs w35] | high | pending |
| 10 | `PreModelSwitch` / `PostModelSwitch` hooks | New hook events fire before and after a model switch. `PreModelSwitch` can block the switch; `PostModelSwitch` can inject context after the switch. Enables model-governance and context-injection patterns in autonomous sessions. | https://code.claude.com/docs/en/hooks#premodelswitch | WATCH — [VERIFIED: official docs w36] | high | pending |
| 11 | `maxEffortLevel` setting | Caps effort level across all providers including Bedrock, GCP, and Foundry. Can be set at top level or per-model under `modelSettings`. Prevents runaway compute in autonomous sessions that might escalate effort level. | https://code.claude.com/docs/en/settings-reference#maxeffortlevel | WATCH — [VERIFIED: official docs w37] | high | pending |
| 12 | Claude Fable 5.1 | New model in Claude Code with 1M-token context window. `fable` alias selects it. Available via `/model fable`. Requires v2.1.257+. | https://code.claude.com/docs/en/whats-new/2026-w36 | WATCH — [VERIFIED: official docs w36] | high | pending |
| 13 | Plugin marketplace `command` sources | Plugin marketplaces accept `command` sources: a local command prints the plugin directory, re-resolved every session without a restart. Enables dynamic, environment-aware plugin resolution. | https://code.claude.com/docs/en/plugin-marketplaces#command-sources | WATCH — [VERIFIED: official docs w33] | medium | pending |
| 14 | Eval-driven agent self-improvement loop | Research pattern: harness engineering + telemetry traces + LLM-as-judge grading + automated retraining loop enables agents to self-improve across runs. Distinct from autoresearch — focuses on improving the agent's *skill routing and execution quality* rather than its knowledge. | https://arxiv.org/pdf/2607.07663 | TEST — [UNVERIFIED: research paper; pattern extractable natively] | medium | pending |
| 15 | `/usage` Loops breakdown | `/usage` adds a Loops breakdown: run count, total tokens, tokens per run, and last run for the most token-heavy `/loop` and scheduled tasks. Available on Pro/Max/Team/Enterprise. Directly applicable to monitoring compound-brain routines. | https://code.claude.com/docs/en/costs#plan-usage-breakdown | WATCH — [VERIFIED: official docs w35] | high | pending |

---

## Patterns Worth Knowing

### 1. `claude plugin eval` as the Skill Quality Gate

`claude plugin eval` turns skill quality from subjective to measurable. The `tool_used: Skill` grader specifically checks whether a natural-language prompt routes to the intended skill — the most common failure mode in compound SKILL.md ecosystems. The pattern: write a suite of realistic prompts, run `claude plugin eval init` to get graders drafted, then run `claude plugin eval .` before merging any skill changes. Exit codes make CI integration straightforward. Every run is a real model call on your account, so keep suites lean (3 cases per skill is often enough to catch routing failures).

### 2. `/skill-doctor` as the Skill Context Budget Auditor

Every enabled skill adds tokens to every session regardless of invocation. `/skill-doctor` surfaces which skills cost the most and which are never used — the exact information needed to justify trimming. In a compound-brain installation with 5–10 skills loaded by default, unused skills can silently consume 5–15% of context before the first turn. Running `/skill-doctor` before any skill addition or refactor gives a baseline.

### 3. `--restricted` + `--tools` as the Evaluation Harness Pattern

The `--restricted` flag removes all dangerous tools (Bash, WebFetch, computer-use) while the `--tools` allowlist adds specific ones back. The pattern for eval harnesses: `claude --restricted --tools "Read,Write" -p "..."` gives read/write access for analysis tasks without shell access. Safer and more auditable than `--dangerously-skip-permissions` for unattended evaluation runs.

### 4. Task Tools Require an Explicit Re-enable on Newer Models

`TaskCreate`/`TaskUpdate`/`TodoWrite` are silently absent on Sonnet 5, Fable 5, Mythos 5+. This is a behavioral change, not a feature toggle — any workflow or prompt that depended on these tools will appear to succeed while actually doing nothing. The fix is `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` in the environment, or migrating to in-session state management (AGENTS.md-style, queue.md-style). Prior compound-brain conventions that relied on task tools need audit.

### 5. `promptCacheTtl: "1h"` as a Cron Session Cost Reducer

Scheduled routines fire into a fresh session with a cold context. Setting `promptCacheTtl: "1h"` in user settings warms the cache for the main conversation; if the routine runs again within the hour (e.g., re-triggered on failure), the second run pays only for uncached tokens. At 1M-token context budgets, a cache miss can be expensive. One setting, persistent benefit.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| `claude plugin eval` with `tool_used: Skill` grader | `plugins/compound-brain/` skills | Quantifies whether skill routing works before merging; makes skill descriptions testable, not just descriptive |
| `/skill-doctor` audit | All enabled skills | Baseline context cost per skill; justify trimming unused skills; run before adding new ones |
| `--restricted` mode | Weekly digest routine, eval harnesses | Safer unattended execution without shell access; removes WebFetch misuse risk in cloud sessions |
| `promptCacheTtl: "1h"` | User settings | Reduces cost of routine cold-starts; especially useful for the weekly digest routine which loads a large CLAUDE.md |
| `maxEffortLevel` in settings | All autonomous routines | Hard ceiling on compute spend; prevents escalation to xhigh/max in unattended sessions |
| Task tools opt-in flag | queue.md-style workflows | Audit all existing workflows for silent task-tool failure on Sonnet 5+; migrate or add the env var |
| `@` session mentions + `SendMessage` | Multi-session orchestration | Research lanes can pass findings to a coordinator session directly, without file-based coordination |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Write digest outcomes for confirmed prior findings

**Risk: SAFE** — markdown edits under `.brain/knowledge/research/`

Prior digests have ADOPT items with `outcome: pending` that are now confirmed or need status update:
- 2026-08-04 #6 (Anti-fabrication notifications): confirmed in AGENTS.md as of that run
- 2026-08-04 #1 (/doctor): confirmed verified; usage still pending (not run in this repo yet)
- 2026-08-03 #1 (Ralph Loop): confirmed in AGENTS.md as of 2026-08-04

Outcome edits applied below in Step 5 bookkeeping.

### [SAFE-2] Add queue item for task-tools audit

**Risk: SAFE** — append to `.brain/queue.md`

Task tools (`TaskCreate`, `TaskUpdate`, `TodoWrite`) are silently unavailable on Sonnet 5, Fable 5+. This routine itself may be affected if it references those tools. Add a queue item to audit all `.brain/routines/` prompts and skills for task-tool reliance. SAFE to write to queue.

### [SAFE-3] Add queue item to run `/skill-doctor`

**Risk: SAFE** — append to `.brain/queue.md`

`/skill-doctor` surfaces context cost per skill. With 5+ skills enabled in this repo's plugin, this is high-value before adding more. Add queue item to run it in a live session and log the output to `.brain/knowledge/resources/skill-doctor-baseline.md`.

### [SAFE-4] Note `promptCacheTtl` opportunity in brain upgrade notes

**Risk: SAFE** — markdown append to `.brain/knowledge/resources/`

Draft a note for the operator: adding `promptCacheTtl: "1h"` to user settings reduces cold-start cost for weekly routines. Applied in this run.

---

## Recommended Actions

1. **Run `claude plugin eval init` on the compound-brain plugin.** `claude plugin eval` is the most structurally significant new tool for this brain: it makes skill routing testable. The brain ships skills as a plugin (`plugins/compound-brain/`). Run `claude plugin eval init` in that directory, let it draft the suite, then run `claude plugin eval .` to get a baseline before the next skill change. This is a low-risk, high-signal action that has been SAFE since v2.1.269.

2. **Audit routines for task-tool reliance before the next scheduled run.** `TaskCreate`/`TaskUpdate`/`TodoWrite` are silently absent on Sonnet 5, Fable 5+. The weekly digest routine runs in a cloud session on whatever model the session defaults to. If any prompt or skill references these tools, the failure is silent. Audit `.brain/routines/` and `plugins/compound-brain/skills/` for task-tool calls. Add `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` to the routine's environment or migrate to queue.md-style state management.

3. **Set `maxEffortLevel` in user settings to cap autonomous session compute.** Autonomous sessions (cron, scheduled routines) can escalate effort level without bound. `maxEffortLevel` provides a hard cap across all providers. This is a one-line settings change that prevents runaway cost. Needs approval to touch settings.

---

## Needs Approval

- **Set `promptCacheTtl: "1h"` in user settings** — reduces weekly routine cold-start cost; requires editing user settings
- **Set `maxEffortLevel`** in user or managed settings to cap autonomous session compute — requires editing settings
- **Run `claude plugin eval init` in `plugins/compound-brain/`** — read-only audit, but the `init` subcommand starts an interactive session and writes eval files; review output before committing
- **Add `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` to routine environment** — requires editing hooks, cron config, or settings
- **Audit and update `.claude/hooks/`** for `PreModelSwitch`/`PostModelSwitch` opportunities — hooks require approval
- **Delete public branch `claude/cool-heisenberg-2iokix`** (queue item 006) — owner action; still pending
- **Decide repo visibility: public → private** (queue item 007) — still pending; this digest, like prior ones, contains no private names, but the brain architecture itself is sensitive
