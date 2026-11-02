# LLM Architecture Digest: 2026-11-02

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** Covers official Claude Code releases w32–w37 (Aug 3 – Sep 11, 2026) and community research
(Aug–Nov 2026). Prior digest cut off at Aug 4, so w32 is partially new. No prior finding is re-reported.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | Task tools disabled on newer models | TaskCreate, TaskUpdate, TodoWrite, and related task-tracking tools are no longer available on Opus 4.8, Sonnet 5, Fable 5, Mythos 5, and later. Set `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` to re-enable them. Affects every session running a recent model — including this brain's scheduled runs. | https://code.claude.com/docs/en/tools-reference.md#task-tool-availability | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 2 | /skill-doctor — per-skill context cost audit | Shows context tokens consumed by each loaded skill and how often it has been used, so unused skills can be turned off. Every skill in the listing adds to context on every turn. Run in interactive mode opens the Stats tab; `-p` mode prints a text report. | https://code.claude.com/docs/en/skills.md#find-unused-skills | ADOPT — [VERIFIED: official docs w36] | high | pending |
| 3 | Cross-session messaging + @ mention | Sessions can message each other via `@session-name` in the prompt or the `SendMessage` tool. Bare names that match exactly one live session deliver without confirmation. Interactive sessions auto-get unique names to avoid collision. Messaging is also available on Bedrock/GCP/Foundry from w35. | https://code.claude.com/docs/en/cross-session-messaging.md | ADOPT — [VERIFIED: official docs w32/w33] | high | pending |
| 4 | Fork mode on by default (interactive) | Claude can now request the `fork` subagent type in interactive sessions, inheriting full conversation + prompt cache instead of starting fresh. Subagents Claude spawns in interactive sessions also run in background by default. Disable with `CLAUDE_CODE_FORK_SUBAGENT=0`. | https://code.claude.com/docs/en/sub-agents.md#turn-fork-mode-on-or-off | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 5 | promptCacheTtl per session | `promptCacheTtl: "1h"` holds a one-hour prompt cache on the main conversation when using an API key or cloud provider. `subagentPromptCacheTtl` sets the TTL for subagents. Directly controls cost on long-running or scheduled sessions. | https://code.claude.com/docs/en/prompt-caching#choose-the-ttl-yourself | ADOPT — [VERIFIED: official docs w35] | high | pending |
| 6 | --restricted mode for eval harnesses | Starts Claude Code without Bash, WebFetch, and without user/project settings. Confines file tools to working directories. For evaluation or read-only review tasks on shared machines. Restore individual tools with `--tools "Bash,Read,Edit"`. | https://code.claude.com/docs/en/cli-reference.md#cli-flags | TEST — [VERIFIED: official docs w35] | high | pending |
| 7 | claude plugin eval — evals for plugins | Runs a plugin against a test suite, scores results, and compares against a no-plugin baseline. `claude plugin eval init` drafts cases and graders. Every run is a real model call. Directly applicable to compound-brain skills via the plugin architecture. | https://code.claude.com/docs/en/plugin-evals.md | TEST — [VERIFIED: official docs w37] | high | pending |
| 8 | PreModelSwitch + PostModelSwitch hooks | New hook types: `PreModelSwitch` can block a requested model change; `PostModelSwitch` can inject context after the model changes. Enables governance over which models autonomous sessions can use. | https://code.claude.com/docs/en/hooks#premodelswitch | TEST — [VERIFIED: official docs w36] | high | pending |
| 9 | Auto mode /permissions tab + Auto-continue on Desktop | `/permissions` now has an Auto mode tab to view and edit classifier rules without opening settings files. Desktop's session-limit card offers Auto-continue checkbox that retries on reset. `/permissions` edit is SAFE; Auto-continue is Desktop-only. | https://code.claude.com/docs/en/auto-mode-config.md#edit-rules-from-permissions | TEST — [VERIFIED: official docs w35/w33] | high | pending |
| 10 | bypassPermissions blocked in project settings | `defaultMode: "bypassPermissions"` in a project's `.claude/settings.json` or `.local.json` no longer takes effect (security improvement from w36). Now requires user or managed settings, or the `--permission-mode` flag. | https://code.claude.com/docs/en/permission-modes.md#which-mode-a-session-starts-in | ADOPT — [VERIFIED: official docs w36] | high | pending |
| 11 | managedMcpServers — org-wide MCP push | Organizations can list HTTP and SSE MCP servers under `managedMcpServers` in managed settings to push them to every user, complementing user-added servers. | https://code.claude.com/docs/en/managed-mcp#provide-servers-through-managed-settings | WATCH — [VERIFIED: official docs w36] | high | pending |
| 12 | Claude Fable 5.1 | New model with 1M context, available via `fable` alias in Claude Code (v2.1.257+). Enterprise seat defaults moved to Opus 5. | https://code.claude.com/docs/en/model-config.md#work-with-fable | WATCH — [VERIFIED: official docs w36] | high | pending |
| 13 | /design research preview | Artboard workflow in CLI and Desktop: Claude drafts editable UI artboards and implements the one you pick. Built on artifacts. Research preview. | https://code.claude.com/docs/en/whats-new/2026-w34.md | WATCH — [VERIFIED: official docs w34] | medium | pending |
| 14 | /diff live panel | In fullscreen rendering, `/diff` opens a side panel that refreshes on each file edit or shell command, showing changed files + line counts. Select lines to attach to next prompt. | https://code.claude.com/docs/en/interactive-mode.md#diff-panel | WATCH — [VERIFIED: official docs w36] | high | pending |
| 15 | Subagent maxTurns resume via SendMessage | A subagent that stops at its `maxTurns` limit now returns partial output with a hint that the parent can continue it via `SendMessage`, instead of appearing finished. Critical for long-running research subagents. | https://code.claude.com/docs/en/sub-agents#resume-subagents | ADOPT — [VERIFIED: official docs w35] | high | pending |

---

## Patterns Worth Knowing

### 1. Task Tools Are Gone on Modern Models — Queue Pattern Needs Adaptation

From w33, TaskCreate, TaskUpdate, TodoWrite, and related tools are disabled on Opus 4.8, Sonnet 5, Fable 5, Mythos 5, and later. The compound-brain scheduled routine likely runs on Sonnet 5 or newer, meaning the queue.md pattern (markdown-native) is the right solution — not those tools. The system reminder in this session confirms they are "deferred" (not removed, but not default). The SAFE path: continue using markdown queue.md and AGENTS.md as the primary state layer. The `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` flag can re-enable them, but the markdown approach is more durable across model upgrades.

### 2. /skill-doctor Solves the CLAUDE.md Skill Overhead Problem

Every skill adds context tokens on every turn, whether or not Claude uses it. `/skill-doctor` quantifies this cost per skill and tracks usage frequency. For compound-brain, running `/skill-doctor` before queue-002 (CLAUDE.md audit) is even more valuable than running `/doctor` first — it targets the skill overhead problem that compounds across every session. Running it in `-p` mode produces a text report without opening the UI.

### 3. Cross-Session Messaging Enables Native Multi-Agent Pipelines

Sessions can now address each other by name via `@session-name` or the `SendMessage` tool. Combined with fork mode being on by default (fork inherits full conversation + cache), compound-brain can now split research into parallel named lanes that report back to a coordinator session. This is the native primitive that replaces the manual WorkerAgent pattern from prior research.

### 4. promptCacheTtl Reduces Cost on Scheduled Runs

Scheduled sessions start fresh, wasting the prompt cache. Setting `promptCacheTtl: "1h"` in settings keeps the cache warm for the main conversation. For the weekly digest routine that reads several files at session start, this cuts the cost of re-reading AGENTS.md and queue.md on repeated invocations within an hour. `subagentPromptCacheTtl` applies the same logic to forks and subagents.

### 5. The bypassPermissions Project Setting Is Silently Neutered

Any project that used `defaultMode: "bypassPermissions"` in project settings now silently falls back to Manual. This is a security improvement, but it means any compound-brain config that relied on project-level bypass is silently less permissive. Check `.claude/settings.local.json` for this pattern.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| /skill-doctor audit | CLAUDE.md + loaded skills | Quantifies context overhead per skill before queue-002 manual audit; informs which skills to disable vs keep |
| Task tools guard | All routines | Add `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` note to queue.md or consider committing it to project settings so deferred task tools are available when needed |
| promptCacheTtl | Scheduled digest routine | Setting `promptCacheTtl: "1h"` in project settings reduces per-run cost for sessions that re-read brain files |
| PreModelSwitch hook | Governance | Block unauthorized model switches in autonomous sessions — prevents a cron session from accidentally switching to a more expensive model mid-run |
| claude plugin eval | compound-brain plugin | Draft eval suites for brain skills to validate they contribute measurable quality improvement vs baseline; aligns with the validate-digest skill (queue 003) |
| Cross-session @mention | Research lanes | Name research subagents and have them report back by session name, enabling coordinator pattern without manual hand-off |
| Subagent maxTurns resume | Weekly research routine | If research forks hit their turn limit, the parent can resume them via SendMessage instead of silently losing results |
| bypassPermissions check | Security | Audit `.claude/settings.local.json` for any `bypassPermissions` project setting that is now silently neutered |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Update Prior Digest Outcome Fields

**Risk: SAFE** — markdown edit under .brain/knowledge/research/

Items from 2026-08-04 that are now confirmed or updated:
- ADOPT-6 (Anti-fabrication notifications): CONFIRMED — this session's system reminder includes the anti-fabrication language
- All ADOPT items from 2026-08-04 remain pending (no contradicting evidence found this run)

Applied immediately below in this session.

---

### [SAFE-2] Add Queue Items for New Findings

**Risk: SAFE** — markdown appends to .brain/queue.md

Add:
- Item 013: Run `/skill-doctor` and document skill context costs — prerequisite for queue-002 CLAUDE.md audit
- Item 014: Audit `.claude/settings.local.json` for neutered `bypassPermissions`
- Item 015: Consider adding `promptCacheTtl: "1h"` to project settings — reduces scheduled run cost (NEEDS APPROVAL to touch settings)

---

### [SAFE-3] Append Learning to AGENTS.md

**Risk: SAFE** — append to .brain/AGENTS.md

Key new learning: Task tools (TaskCreate/TaskUpdate/TodoWrite) are disabled by default on Sonnet 5/Opus 4.8/Fable 5 and later. The compound-brain markdown queue pattern is the right fallback and already in use.

---

## Recommended Actions

1. **Run `/skill-doctor -p` before queue-002 CLAUDE.md audit.** `/skill-doctor` prints per-skill context cost and usage frequency as a text report in non-interactive mode. This is the right prerequisite for queue-002 — it tells you which skills are dead weight before you trim CLAUDE.md manually. Cheaper than `/doctor` and more targeted. Queue item 013.

2. **Audit `.claude/settings.local.json` for `bypassPermissions`.** The w36 change silently neutered project-level `defaultMode: "bypassPermissions"`. If any brain session relied on that, it is now running in Manual mode without warning. Check and update if needed. Queue item 014. NEEDS APPROVAL to change settings.

3. **Add `promptCacheTtl: "1h"` to project settings or managed settings.** Scheduled runs re-read brain files on every invocation. A 1-hour TTL keeps the main conversation cache warm, cutting per-run cost. Draft the setting change for approval. Queue item 015.

---

## Needs Approval

- **`promptCacheTtl` setting addition** — touching `.claude/settings.json` or managed settings requires approval
- **`CLAUDE_CODE_ENABLE_TODO_TOOLS=1`** — adding this to environment or settings requires approval
- **`PreModelSwitch` hook for model governance** — touching `.claude/hooks/` requires approval
- **Drafting `claude plugin eval` suites for brain skills** — SAFE as markdown drafts under `.brain/candidate-skills/`; running them is a model call requiring approval
- **Fixing any neutered `bypassPermissions` config** — touching settings requires approval
- **queue-002 (CLAUDE.md split)** — remains blocked pending /skill-doctor run and owner approval
