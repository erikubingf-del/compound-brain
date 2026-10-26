# LLM Architecture Digest: 2026-10-26

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** 4-lane scan covering official Claude Code releases weeks 32–37 (Aug 3 – Sep 11, 2026), third-party ecosystem (agnix, hcom, VibeMemBench), and academic memory architecture papers. Last digest was 2026-08-04. Weeks 38+ are not yet published. This is the first digest in ~12 weeks; the gap covers significant platform changes.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | Cross-Session Messaging (ListAgents + SendMessage) | Sessions on the same machine can discover each other with `ListAgents` and send messages with `SendMessage`. Claude passes findings or decisions between sessions without human re-entry. `@session-name` in the prompt delivers directly. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 2 | /skill-doctor — Skill Cost & Usage Audit | Shows what each installed skill costs in context tokens and how often it fires. Every skill adds to context on every turn even if never used. Surfaced in `/plugin` Stats tab. Critical for keeping routine context budgets lean. | https://code.claude.com/docs/en/whats-new/2026-w36 | ADOPT — [VERIFIED: official docs w36] | high | pending |
| 3 | Task Tools Removed on Newer Models | `TaskCreate`, `TaskUpdate`, `TodoWrite` and related task-tracking tools are no longer available by default on Opus 5, Sonnet 5, Fable 5, Mythos 5, and later families. Any routine or skill that calls these tools on a new model silently gets no-tool. Re-enable with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`. | https://code.claude.com/docs/en/whats-new/2026-w33 | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 4 | promptCacheTtl: 1h Setting | `promptCacheTtl: "1h"` keeps the main conversation's prompt cache for one hour when using an API key or cloud provider. `subagentPromptCacheTtl` sets it separately for subagents. Makes long-running scheduled routines dramatically cheaper. | https://code.claude.com/docs/en/whats-new/2026-w35 | ADOPT — [VERIFIED: official docs w35] | high | pending |
| 5 | Subagent maxTurns Partial Resume | A subagent that hits its `maxTurns` limit now returns its output marked partial with a hint that it can be continued via `SendMessage`, instead of silently appearing finished. Enables long research tasks split across subagent runs. | https://code.claude.com/docs/en/whats-new/2026-w35 | ADOPT — [VERIFIED: official docs w35] | high | pending |
| 6 | Ultraplan Removed (Use Plan Mode or Web) | The `/ultraplan` command and `ultraplan` keyword are removed from Claude Code. The research preview ended. Use plan mode or Claude Code on the web instead. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | confirmed |
| 7 | --restricted Mode for Eval Harnesses | `--restricted` (or `CLAUDE_CODE_RESTRICTED=1`) starts Claude Code without command-running tools, confines file tools to working directories, blocks `bypassPermissions`, and loads only managed settings. For evaluation harnesses on shared machines or ephemeral runners. | https://code.claude.com/docs/en/whats-new/2026-w35 | WATCH — [VERIFIED: official docs w35] | high | pending |
| 8 | Fork Mode On by Default | Fork mode is on by default in interactive sessions. Subagents spawned by Claude can inherit the full conversation and prompt cache instead of starting fresh. `/subtask` triggers a fork that knows everything discussed so far. Turn off with `CLAUDE_CODE_FORK_SUBAGENT=0`. | https://code.claude.com/docs/en/whats-new/2026-w33 | WATCH — [VERIFIED: official docs w33] | high | pending |
| 9 | Concise Output Style | Built-in output style that leads with results, skips preamble and narration. Set via `"outputStyle": "Concise"` in settings or `/config`. Works as written evidence that verbose outputs aren't Claude's unavoidable default — a settings flag controls it. | https://code.claude.com/docs/en/whats-new/2026-w34 | WATCH — [VERIFIED: official docs w34] | high | pending |
| 10 | PreModelSwitch / PostModelSwitch Hooks | Two new lifecycle hook events: `PreModelSwitch` can block a model change; `PostModelSwitch` can inject context after the model changes. Enables enforcing model policy from hooks, or loading model-specific context on switch. | https://code.claude.com/docs/en/whats-new/2026-w36 | WATCH — [VERIFIED: official docs w36] | high | pending |
| 11 | claude plugin eval | `claude plugin eval` runs a plugin against test cases, scores with and without the plugin, and shows the delta. `claude plugin eval init` drafts test cases. Quantifies whether a skill/plugin actually improves outcomes. | https://code.claude.com/docs/en/whats-new/2026-w37 | WATCH — [VERIFIED: official docs w37] | high | pending |
| 12 | bypassPermissions Blocked in Project Settings | Setting `"defaultMode": "bypassPermissions"` in a project's `.claude/settings.json` or `.claude/settings.local.json` no longer takes effect — the session starts in Manual mode. Must be in user or managed settings, or passed via `--permission-mode`. Closes a privilege-escalation path via checked-in settings. | https://code.claude.com/docs/en/whats-new/2026-w36 | WATCH — [VERIFIED: official docs w36] | high | pending |
| 13 | agnix — Agent Config Linter | Third-party CLI linter for SKILL.md, CLAUDE.md, hooks, MCP configs, and AGENTS.md. `agnix .` validates the project, `agnix --fix .` auto-fixes, `agnix --target claude-code .` applies Claude Code rules only. SARIF output for GitHub code scanning. Rule count varies by version (v0.59.0 lists 702). | https://unpkg.com/agnix@0.59.0/README.md | WATCH — [UNVERIFIED: third-party; check official repo before relying on rule counts] | medium | pending |
| 14 | VibeMemBench — Coding Agent Memory Benchmark | arxiv 2609.23570. Benchmarks memory systems for coding agents on real repository tasks. Solver pool omits frontier proprietary models (budget constraint) but supplies task histories, executable predicates, and intervention protocols with full provenance. Useful for validating memory architecture choices. | https://arxiv.org/pdf/2609.23570 | WATCH — [UNVERIFIED: arxiv preprint; not independently run] | medium | pending |
| 15 | Self-Hosted Environments (Public Beta) | Organizations can run Claude Code cloud sessions on their own infrastructure. `claude self-hosted-runner` turns machines into runners. Sessions run inside the org's network with access to internal services. Team and Enterprise, public beta. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |

---

## Patterns Worth Knowing

### 1. Session Messaging Replaces Third-Party Agent Buses

Cross-session messaging (w32) makes `ListAgents` + `SendMessage` the native primitive for orchestrating peer sessions. The prior pattern — using a third-party agent bus (like hcom) wired through hooks — now has a first-party alternative that requires zero infrastructure. A weekly digest routine can fork 4 research lanes via `/fork`, let them run in background, then use `SendMessage` to collect findings into a synthesis session. This is the native realization of the Ralph Loop at multi-session scale.

### 2. Skill Bloat is Now Measurable

`/skill-doctor` (w36) surfaces what was previously invisible: every installed skill pays a context-token tax on every turn, whether or not it fires. This changes the economics of skill design — adding a skill is no longer free. The right operating posture is to run `/skill-doctor` periodically and prune skills whose context cost exceeds their benefit, measured by how rarely they fire. For compound-brain: the plugin ships multiple skills; some may be paying cost every routine turn without value.

### 3. Task Tools Are Silently Gone on New Models

The removal of `TaskCreate`, `TaskUpdate`, and `TodoWrite` on Sonnet 5+/Opus 5+/Fable 5+ (w33) is the highest-risk behavioral change in this digest. Any skill, hook, or routine that relied on these tools to track progress now silently gets no tool. The failure mode is not an error — the model simply doesn't have the tool and can't call it. `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` restores them. Audit every routine and skill that mentions task tracking.

### 4. Project Settings Can No Longer Self-Escalate

bypassPermissions blocked in project `.claude/settings.json` (w36) closes a path where a checked-in settings file could grant a cloned repo's session unrestricted tool access. The trust model is now: user/managed settings control escalation; project settings can only restrict. This is the right architecture for a public brain repo — a settings file in the repo checkout cannot grant itself privileges.

### 5. Prompt Cache TTL is Now Explicit

Before w35, prompt cache duration was implicit. `promptCacheTtl: "1h"` makes it explicit and extends cache reuse across turns in long sessions. For scheduled routines that re-read the same files (AGENTS.md, queue.md, prior digests), setting this means the second read in a session is cache-served, not re-tokenized. This is a direct cost reduction with zero behavioral change.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| Cross-session messaging | Weekly digest routine (parallel research lanes) | Fork 4 search lanes, collect via SendMessage; eliminates sequential search bottleneck |
| /skill-doctor | Plugin skill inventory | Run /skill-doctor to identify which brain skills are paying context cost without value; prune unused ones |
| Task tools removal audit | All routines and skills | Audit for TaskCreate/TaskUpdate usage; add CLAUDE_CODE_ENABLE_TODO_TOOLS=1 to environment or stop relying on task tools |
| promptCacheTtl: 1h | Scheduled routines | Set in API-key or cloud-provider sessions to cache-serve repeat file reads; reduce token cost per digest run |
| Plugin eval | Plugin skill quality | `claude plugin eval init` to draft a test suite for brain skills; quantify whether each skill improves outcomes |
| PreModelSwitch hook | Session model policy | Use hook to enforce or log model changes within brain sessions; catch unexpected model downgrades |
| Concise output style | All routine outputs | Set `outputStyle: Concise` for routine sessions to reduce token waste on narration |
| bypassPermissions change | Security model | Confirms current design is sound — checked-in settings cannot self-escalate; no action needed, just awareness |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Add Queue Items for This Run's Findings

**Risk: SAFE** — markdown append to .brain/queue.md

New queue items to add:
- 012: Audit routines/skills for TaskCreate/TaskUpdate usage — models Sonnet 5+/Opus 5+/Fable 5+ no longer have these by default; add env var or remove calls. High priority.
- 013: Run /skill-doctor to audit plugin skill context cost. Medium priority.
- 014: Set `promptCacheTtl: "1h"` in settings for API/cloud sessions. NEEDS APPROVAL (settings change).
- 015: Evaluate forked parallel research lanes for weekly digest (cross-session messaging). Medium priority.
- 016: Evaluate `claude plugin eval init` to create test cases for brain skills. Low priority.

Applied in Step 5. ✅

---

### [SAFE-2] Update AGENTS.md with Run Learnings

**Risk: SAFE** — markdown append to .brain/AGENTS.md

3 learnings from this run. Applied in Step 5. ✅

---

### [SAFE-3] Update Prior Digest Outcome Fields

**Risk: SAFE** — markdown update under .brain/**

From 2026-08-04 digest:
- Item 2 (Stacked Skill Invocations): still pending — no use yet
- Item 4 (/fork vs /subtask): CONFIRMED as of w33 — fork mode on by default in interactive sessions; `/subtask` triggers fork that inherits full conversation
- Item 7 (Session-Wide Caps): PARTIALLY INVALIDATED — 200-subagent cap was removed in w32; the subagent concurrency and depth limits still apply. WebSearch cap status unconfirmed from official docs.
- Item 6 (Ultraplan removed): CONFIRMED in w32 — `/ultraplan` is gone; queue item for Ultraplan-based planning should be marked superseded

Updated outcome fields in 2026-08-04 digest inline. ✅

---

### [NEEDS APPROVAL] All Other Items

See Needs Approval section below.

---

## Recommended Actions

1. **Audit all routines and skills for TaskCreate/TaskUpdate usage (queue 012).** This is the highest-risk behavioral change. Sonnet 5, Opus 5, and Fable 5 silently lack these tools. The brain's scheduled routines and CLAUDE.md guidance both reference task tracking patterns. Find every occurrence and either add `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` to the execution environment or rewrite to use queue.md-based tracking (the queue.md pattern is already in place and is safer than tool-dependent task tracking anyway). This is SAFE to audit; environment-variable addition NEEDS APPROVAL.

2. **Run /skill-doctor before the next development session (queue 013).** Each brain plugin skill pays a context-token cost on every turn. Run `/skill-doctor` to see which skills actually fire vs. which are deadweight. Pruning unused skills reduces context waste for every future session. This is a CLI command — no file changes, no approval needed.

3. **Add promptCacheTtl: "1h" to settings for API/cloud routine sessions (queue 014).** Scheduled digest runs re-read the same files (AGENTS.md, queue.md, two prior digests) on every run. With `promptCacheTtl: "1h"`, re-reads within the session are cache-served. Direct cost reduction. NEEDS APPROVAL (touches settings).

---

## Needs Approval

- **Add `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`** to routine execution environment — touches hooks, scripts, or runner configuration
- **Set `promptCacheTtl: "1h"`** in settings (queue 014) — touches `.claude/settings.json` or similar
- **Set `outputStyle: Concise`** in settings (queue 015) — touches settings
- **Test cross-session messaging** in a real multi-session routine setup — architectural change to how the weekly digest runs its research lanes; touches routine design
- **Run `claude plugin eval init`** for brain skills (queue 016) — requires a live session with the plugin active and makes real API calls
- **Any model policy enforcement via PreModelSwitch hook** — touching `.claude/hooks/` requires approval
