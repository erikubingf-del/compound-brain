# LLM Architecture Digest: 2026-09-28

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** 4-lane research scan covering weeks 30–37 (July 20 – September 11, 2026).
Prior digests covered through w29 (July 13–17). No findings duplicated from 2026-08-03 or 2026-08-04 digests.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | `claude plugin eval` | Test a plugin against a scored case suite with no-plugin baseline; `claude plugin eval init` drafts cases and graders; `report.html` shows per-run detail. Direct way to prove compound-brain plugin loads and adds value. | https://code.claude.com/docs/en/plugin-evals | ADOPT — [VERIFIED: official docs w37] | high | pending |
| 2 | `/skill-doctor` | Shows context cost and usage frequency for every installed skill; opens in the Stats tab of `/plugin`. Every skill adds to context on every turn whether used or not. Critical for queue 009/010 — audit whether `.claude/skills/` or the plugin skills are loading. | https://code.claude.com/docs/en/skills#find-unused-skills | ADOPT — [VERIFIED: official docs w36] | high | pending |
| 3 | Task tools disabled on newer models | `TaskCreate`, `TaskUpdate`, `TodoWrite` are no longer available on Opus 4.8, Sonnet 5, Fable 5, Mythos 5, and later. Set `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` to re-enable. Brain routines using `.brain/queue.md` directly (not task tools) are unaffected; confirm any skills that referenced these tools. | https://code.claude.com/docs/en/tools-reference#task-tool-availability | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 4 | Cross-session messaging | Sessions on the same machine discover each other via `ListAgents` and message via `SendMessage`. Type `@session-name` in the prompt to mention a session directly. `notify_when_idle` input lets one session signal another when it goes idle. Available on macOS, Linux, Windows (v2.1.224+). | https://code.claude.com/docs/en/cross-session-messaging | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 5 | Auto mode as default | As of August 14, auto mode is the default for Pro/Max/Team new sessions. Auto mode classifier calls no longer count toward usage limits. Permission strategy for all autonomous brain routines changes: the classifier replaces per-prompt approval for safe actions. | https://code.claude.com/docs/en/permission-modes | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 6 | `promptCacheTtl` + `subagentPromptCacheTtl` | Set `promptCacheTtl` to `"1h"` to keep a one-hour prompt cache on the main conversation; `subagentPromptCacheTtl` sets the TTL for subagents and all other requests. Directly controls the cache efficiency the weekly routine depends on. | https://code.claude.com/docs/en/prompt-caching#choose-the-ttl-yourself | ADOPT — [VERIFIED: official docs w35] | high | pending |
| 7 | Fork mode on by default | From w33, `/subtask` (fork subagent) inherits the full conversation and prompt cache instead of starting fresh. Background subagents in interactive sessions also run in background by default. Turn off with `CLAUDE_CODE_FORK_SUBAGENT=0`. Changes subagent orchestration strategy for brain. | https://code.claude.com/docs/en/sub-agents#turn-fork-mode-on-or-off | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 8 | `/fork` changes in own worktree | Background sessions launched with `/fork` now make code changes in their own worktree (not the parent's checkout), auto-commit/push when done, and open a draft PR only when the task explicitly calls for one. Resolves the "auto-PR on every background task" concern. | https://code.claude.com/docs/en/agent-view#how-file-edits-are-isolated | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 9 | `--restricted` mode | Starts a session without command-running tools, WebFetch, or user/project settings; confines file tools to working directories; refuses `bypassPermissions`. For evaluation harnesses and safety-bounded scripted runs. | https://code.claude.com/docs/en/cli-reference#cli-flags | WATCH — [VERIFIED: official docs w35] | high | pending |
| 10 | `maxEffortLevel` setting | Caps the effort level on every provider (including Bedrock, GCP, Foundry); per-model override via `modelSettings`. Limits cost on autonomous sessions that might otherwise ratchet to xhigh effort. | https://code.claude.com/docs/en/settings-reference#maxeffortlevel | WATCH — [VERIFIED: official docs w37] | high | pending |
| 11 | Claude Security plugin | Multi-agent vuln scan: agents map architecture, build threat model, hunt for vulnerabilities, independently review findings, write report to `CLAUDE-SECURITY-<timestamp>/`. Scan repo, branch diff, PR, or commit. Patches are reviewed and applied manually. Install: `/plugin install claude-security@claude-plugins-official`. | https://code.claude.com/docs/en/claude-security | WATCH — [VERIFIED: official docs w30] | high | pending |
| 12 | Claude Fable 5.1 | New model available in Claude Code, 1M context; alias `fable`. Enterprise seats default to Opus 5 (w36). Weekly routine currently configured for Sonnet 4.6. No model migration needed now; note for future. | https://code.claude.com/docs/en/model-config#work-with-fable | WATCH — [VERIFIED: official docs w36] | high | pending |
| 13 | 200-subagent cap removed | The per-session subagent count limit is gone. Concurrency limit (20 default, tunable via `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`) and depth limit (5 levels) still apply. Long-running brain sessions with parallel research lanes no longer hit a hard stop. | https://code.claude.com/docs/en/sub-agents#concurrent-subagent-limit | WATCH — [VERIFIED: official docs w32] | high | pending |
| 14 | PreModelSwitch / PostModelSwitch hooks | New hook events: `PreModelSwitch` can block a model switch; `PostModelSwitch` can add context after the model changes. Relevant if compound-brain hooks need to enforce which model runs scheduled routines. | https://code.claude.com/docs/en/hooks#premodelswitch | WATCH — [VERIFIED: official docs w36] | high | pending |
| 15 | Ultraplan removed | The `/ultraplan` command and `ultraplan` keyword are removed as of w32. Official recommendation: use plan mode or Claude Code on the web instead. The 2026-08-03 digest rated Ultraplan ADOPT; that implementation path is now invalid. | https://code.claude.com/docs/en/ultraplan | SKIP — [VERIFIED: removed in official docs w32] | high | invalidated |

---

## Patterns Worth Knowing

### 1. Plugin Evals as a Closed Feedback Loop

`claude plugin eval` closes the loop that was previously missing: a plugin was installed and assumed to work, but there was no way to measure whether it actually improved Claude's behavior vs. a baseline. The eval suite scores each case with and without the plugin and prints the delta. For compound-brain, this means the weekly routine can eventually include a plugin health check — run the suite, check the delta is positive, alert if a skill regressed. `claude plugin eval init` drafts the cases from a description of what "good" looks like, reducing the cost of writing the first suite.

### 2. /skill-doctor as the Missing Instrumentation Layer

The prior digest noted that skills add context on every turn whether used or not and flagged queue 009 (verify plugin loads). `/skill-doctor` answers this directly: it shows each skill's token cost and usage frequency. This is the instrumentation the brain was missing for making principled decisions about which skills to keep active. The right workflow: run `/skill-doctor`, prune zero-usage skills, re-verify with `claude plugin eval`. Queue 009 and 010 can now be resolved methodically.

### 3. Task Tools Gone on Modern Models — Queue.md Was the Right Bet

`TaskCreate`, `TaskUpdate`, `TodoWrite` are disabled on Sonnet 5, Opus 4.8, Fable 5, Mythos 5 and later. The 2026-08-03 decision to use `.brain/queue.md` as the task queue (a plain markdown file claimed and updated by routines) was architecturally correct: it's model-agnostic, survives container teardown, and doesn't depend on ephemeral task-tool state. Any skill that was secretly calling task tools will silently fail on modern models. Audit skills for `TaskCreate` / `TodoWrite` references.

### 4. Fork Mode + Worktree Isolation Changes the Orchestration Model

Two changes together: (1) `/subtask` now inherits the full conversation context instead of starting fresh — a fork subagent knows everything the parent knows; (2) `/fork` background sessions do their work in their own worktree, not the parent's checkout. This resolves the risk of parallel agents clobbering each other's files. For brain improvement work: a background `/fork` session can research and write to its own worktree, then auto-commit and open a draft PR for review. No manual push step needed.

### 5. Auto Mode Default Changes the Permission Trust Baseline

Auto mode is now the default for all Pro/Max/Team sessions. The classifier handles safe actions without prompts and blocks genuinely risky ones. For the weekly digest routine specifically: if settings don't override the mode, the routine now runs in auto mode, which means the "permission setup session" from the 2026-08-04 recommended actions is less urgent — auto mode handles most tool approvals without a one-time setup pass. The key remaining step is auditing what the classifier blocks and adding explicit allow rules for any tool the routine legitimately needs.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| `claude plugin eval` + eval suite | compound-brain plugin | Quantified proof the plugin adds value; regression detection on each push; `claude plugin eval init` drafts first suite from a description |
| `/skill-doctor` audit | `.claude/skills/` vs `plugins/compound-brain/skills/` | Resolve queue 009/010: run once to see which skills are live, what they cost, how often used; prune dead weight |
| Task tools disabled | Skill auditing | Audit every skill for `TaskCreate` / `TodoWrite` calls; replace with queue.md writes or remove if unused |
| `promptCacheTtl: "1h"` | Weekly routine sessions | Keeps context warm for the full routine run; explicitly set `subagentPromptCacheTtl: "5m"` for research subagents that don't need a warm cache |
| Fork mode + worktree isolation | Brain improvement / code work | Use `/fork` for any brain improvement that touches files; gets its own worktree, auto-commits, opens draft PR; no manual push step |
| `maxEffortLevel` cap | All autonomous routines | Set a cap to prevent cron sessions from silently ratcheting to xhigh effort; `"medium"` is appropriate for the weekly digest |
| PreModelSwitch / PostModelSwitch hooks | `.claude/hooks/` | Enforce model on scheduled sessions; add context when model changes mid-session |
| Ultraplan invalidated | 2026-08-03 queue | Remove queue references to Ultraplan; it no longer exists; use plan mode for multi-step planning |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Update Prior Digest Outcome Fields

**Risk: SAFE** — markdown edit under `.brain/`

Update 2026-08-04 digest outcome fields:
- Find #4 (/fork vs /subtask): outcome → `confirmed` — w32/w33 confirmed the architecture; fork now on by default
- Find #5 (Subagents background by default): outcome → `confirmed` — w33 fork mode on by default confirms; background is the new default
- Find #9 (Background Agents Auto-PR on Worktree Completion): outcome → `confirmed-refined` — behavior confirmed but scoped: PR only when task calls for it, not always; worktree isolation now enforced
- Find #15 (Ultraplan removed): this is a new Find #15 in the 2026-08-03 digest; update the ADOPT to `invalidated` — the feature no longer exists

### [SAFE-2] Append Learnings to AGENTS.md

**Risk: SAFE** — append to `.brain/AGENTS.md`

Add a 2026-09-28 entry with the key learnings from this run (see Step 5 bookkeeping below).

### [SAFE-3] Update Queue

**Risk: SAFE** — update `.brain/queue.md`

- Mark queue 012 done.
- Add queue 013: Run `/skill-doctor` and `claude plugin eval init` to measure compound-brain plugin health (NEEDS APPROVAL to execute interactively, but adding to queue is SAFE).
- Add queue 014: Audit all skills for `TaskCreate`/`TodoWrite` references (SAFE to audit; NEEDS APPROVAL to edit skills).
- Remove or update queue 001's Ultraplan reference in the 2026-08-03 context.

### [SAFE-4] Note Task-Tool Removal in AGENTS.md

**Risk: SAFE** — append to `.brain/AGENTS.md`

Append: "`TaskCreate`, `TaskUpdate`, `TodoWrite` disabled on Sonnet 5, Opus 4.8, Fable 5+ as of w33. Brain uses queue.md (unaffected). Audit skills for task-tool references — silent failure on modern models."

---

## Recommended Actions

1. **Run `/skill-doctor` then `claude plugin eval init` in an attended session.** These two commands together answer queue 009 and 010. `/skill-doctor` shows whether `.claude/skills/` or the plugin skills are actually loading and what they cost. `claude plugin eval init` drafts a test suite so plugin health becomes measurable. Both require an interactive session (NEEDS APPROVAL to execute).

2. **Set `promptCacheTtl: "1h"` in user settings.** The weekly routine is exactly the kind of long-running session that benefits from a warm cache. A one-line settings change. NEEDS APPROVAL (touches settings.json).

3. **Set `maxEffortLevel: "medium"` in user settings or as a managed setting.** Cron sessions have no human watching cost accumulate. Capping effort at medium prevents the classifier from silently upgrading to xhigh effort on hard sub-problems. NEEDS APPROVAL (touches settings.json).

---

## Needs Approval

- **Run `/skill-doctor`** — interactive session required; audit output touches skill state
- **Run `claude plugin eval init`** — starts a model session, writes eval files under the plugin; interactive
- **Set `promptCacheTtl` and `subagentPromptCacheTtl`** — modifies `~/.claude/settings.json` or project settings
- **Set `maxEffortLevel`** — modifies settings.json
- **Audit and update hooks for `PreModelSwitch`/`PostModelSwitch`** — touches `.claude/hooks/`
- **Enable `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`** if any skills need it — modifies env/settings
- **Apply `--restricted` to evaluation harnesses** — requires confirming which harnesses exist and how they're launched
