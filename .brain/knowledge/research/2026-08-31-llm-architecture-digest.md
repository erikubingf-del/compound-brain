# LLM Architecture Digest: 2026-08-31

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** 4-lane research scan covering official docs w30–w34 (2026-07-20 through 2026-08-21) plus GitHub trending and community patterns. Prior digests covered through w29 — no re-reporting of those items.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | Cross-session messaging | Claude sessions find each other with `ListAgents` and message with `SendMessage` — text-only, not history or files. Available macOS/Linux/Windows (Windows added w34). One session can pass a finding or a decision to another without human re-explanation. | https://code.claude.com/docs/en/cross-session-messaging | ADOPT — [VERIFIED: official docs w32/w34] | high | pending |
| 2 | `notify_when_idle` on SendMessage | Set `notify_when_idle: true` on a `SendMessage` call and the target session sends one notice back when it next goes idle. Enables handoff coordination: session A dispatches work to session B and gets woken when B is done, without polling. | https://code.claude.com/docs/en/cross-session-messaging#get-a-notice-when-another-session-goes-idle | ADOPT — [VERIFIED: official docs w34] | high | pending |
| 3 | Auto mode is now the default | From August 14, auto mode is the default permission mode for new sessions on Pro, Max, and Team. Auto mode classifier calls no longer count against usage limits. Existing user default settings are preserved unless you accept the one-time switch prompt. | https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 4 | 200-subagent-per-session cap removed | The 200-subagent cap is gone as of w32 (v2.1.220+). Long-running sessions can now spawn subagents without hitting the prior ceiling. Concurrency and depth limits (5 levels) still apply. | https://code.claude.com/docs/en/sub-agents#concurrent-subagent-limit | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 5 | Concise output style | New built-in style: Claude leads with the result and skips preamble/narration. Set via `/config` or `"outputStyle": "Concise"` in settings.json. Error reports, security warnings, and destructive-action confirmations keep full content. v2.1.237+. | https://code.claude.com/docs/en/output-styles#built-in-output-styles | ADOPT — [VERIFIED: official docs w34] | high | pending |
| 6 | `ANTHROPIC_DEFAULT_MODEL` env var | Sets the model new sessions start on without touching CLAUDE.md or settings.json. A `/model` pick still overrides and persists across restarts. Enables model control in routine/cron environments via environment config alone. | https://code.claude.com/docs/en/model-config#set-a-default-model-for-new-sessions | ADOPT — [VERIFIED: official docs w34] | high | pending |
| 7 | Claude Opus 5 | New default Opus model in Claude Code. 1M-token context window. Fast mode at $10/$50/MTok. Replaces Opus 4.8 as default on Max, Team Premium, Enterprise. Context budget calculations should be revisited at 1M scale. | https://code.claude.com/docs/en/whats-new/2026-w30 | ADOPT — [VERIFIED: official docs w30] | high | pending |
| 8 | /code-review runs as background subagent | `/code-review` (and `/review` alias) now dispatches as a background subagent so the main session stays usable during the review. Effort level reuses the last level typed if none is specified. | https://code.claude.com/docs/en/code-review#review-a-diff-locally | ADOPT — [VERIFIED: official docs w30/w32] | high | pending |
| 9 | /goal 30-minute background checkin | When background tasks keep a `/goal` waiting, Claude checks in every 30 minutes instead of waiting indefinitely. Intervals lengthen while the session is idle. Disable with `CLAUDE_CODE_GOAL_CHECKIN_MINUTES=0`. Prevents silent hang of autonomous goal loops. | https://code.claude.com/docs/en/goal#background-work-defers-evaluation | ADOPT — [VERIFIED: official docs w34] | high | pending |
| 10 | /fork now uses its own worktree | A session forked with `/fork` makes its code changes in a worktree of its own instead of the original session's checkout. Eliminates cross-contamination between parent and forked sessions. Combined with the isolation change (Bash and git redirects blocked from reaching main checkout). | https://code.claude.com/docs/en/agent-view#copy-the-session-with-%2Ffork | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 11 | Ultraplan research preview removed | `/ultraplan` command and `ultraplan` keyword are removed as of w32. Use plan mode or Claude Code on the web instead. Any stored prompts, hooks, or CLAUDE.md content referencing `/ultraplan` will now fail silently. | https://code.claude.com/docs/en/whats-new/2026-w32 | SKIP — removal note [VERIFIED: official docs w32] | high | pending |
| 12 | iOS Simulator pane on Desktop | Claude Code Desktop (public beta) opens an iOS Simulator pane — Claude can run your app and tap through it while you watch. Closes the loop for mobile UI verification. | https://code.claude.com/docs/en/whats-new/2026-w30 | WATCH — [VERIFIED: official docs w30] | high | pending |
| 13 | Claude Security plugin | Multi-agent vulnerability scan of the codebase; turns selected findings into patches you apply yourself. Not auto-apply — human reviews and selects. | https://code.claude.com/docs/en/whats-new/2026-w30 | WATCH — [VERIFIED: official docs w30] | high | pending |
| 14 | Self-hosted environments | Run Claude Code cloud sessions on your own infrastructure. `claude self-hosted-runner` turns machines/containers into runners. Sessions start inside your network with access to internal services. Public beta on Team and Enterprise. | https://code.claude.com/docs/en/self-hosted-environments-quickstart | WATCH — [VERIFIED: official docs w32] | high | pending |
| 15 | /design research preview | Artboard workflow in the CLI and Claude Code Desktop. Claude drafts editable UI artboards as artifacts; pick one and have Claude implement it. Pro/Max/Team/Enterprise, v2.1.234+. | https://code.claude.com/docs/en/artifacts#availability | WATCH — [VERIFIED: official docs w34] | high | pending |

---

## Patterns Worth Knowing

### 1. Multi-Session Brain Coordination via Cross-Session Messaging

Cross-session messaging turns independent Claude sessions into a lightweight message-passing system. The pattern for compound-brain: a weekly digest session can fork research lanes into background sessions (`/fork`), each lane writes findings to `.brain/knowledge/research/lanes/`, and uses `notify_when_idle` to signal when done. The orchestrating session wakes, reads all lanes, synthesizes, and commits. No polling — event-driven via the idle notification. This eliminates the current sequential WebSearch pattern and enables true parallel research lanes without Dynamic Workflows.

### 2. Auto Mode as the New Permission Baseline

Auto mode is now the default. This means scheduled/cron sessions no longer need explicit permission grants for routine tool calls — the safety classifier handles them. The important implication: prior AGENTS.md entries about the Bash allowlist being the trust boundary still hold, because auto mode's classifier is the new enforcer, not the explicit `allow/deny` lists. Compound-brain hooks and the write-gate rules remain necessary for the cases the classifier doesn't cover.

### 3. /goal + Checkin Loop as Autonomous Run Pattern

`/goal` (w20) combined with the new 30-minute background checkin (w34) creates a durable autonomous run primitive: define a completion condition in `/goal`, background work proceeds, Claude checks in every 30 minutes, and the goal terminates when the condition holds. This is a native analog to the Ralph Loop pattern already in the brain — but managed by the runtime rather than implemented in a stored prompt. Evaluate whether the weekly routine should migrate to `/goal`-managed execution.

### 4. /fork Worktree Isolation as Safe Parallel Execution

`/fork` now creates its own worktree, meaning parallel research branches don't touch the main checkout's `.brain/` tree. Combined with the reinforced worktree isolation (Bash and git redirects blocked from reaching main checkout as of w32), this makes `/fork`-based parallelism genuinely safe for unattended sessions. The auto-PR behavior (opens a draft PR only when the task calls for one) is now conditional — no more unconditional auto-PR on every completed background session.

### 5. Concise Style + ANTHROPIC_DEFAULT_MODEL as Routine Hygiene

Two small config levers that combine for cleaner cron output: `ANTHROPIC_DEFAULT_MODEL` pins the model per environment without editing any file the brain manages, and `"outputStyle": "Concise"` in settings eliminates narration from scheduled output. Routine output should be findings, not explanation — both levers push in that direction.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| Cross-session messaging + notify_when_idle | Weekly digest routine | Parallelize 4 research lanes into forked sessions; orchestrator wakes on idle signal; eliminates sequential WebSearch bottleneck |
| Auto mode as default | All autonomous routines | Routine sessions no longer need explicit permission grants; reduce settings.local.json allow-list maintenance |
| /goal 30-min checkin | Weekly digest + any long-running routine | Native autonomous loop primitive; replaces stored-prompt Ralph Loop pattern for sessions that can hold a goal condition |
| 200-subagent cap removed | Any multi-lane research run | Can now safely fork unlimited parallel research sessions per week run; depth limit (5 levels) still applies |
| ANTHROPIC_DEFAULT_MODEL | Routine/cron session config | Model pinning per environment without touching CLAUDE.md; good for differentiating routine model from interactive model |
| Concise output style | settings.json for routine sessions | Routine output leads with findings, not narration; easier to scan in weekly digest commits |
| /fork worktree isolation | Any parallel session work | True checkout isolation for parallel lanes; no main-checkout contamination risk |
| Ultraplan removal | Any CLAUDE.md or hook references | Audit for broken `/ultraplan` references — they now fail silently |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Update prior digest outcome field for item #6 (anti-fabrication)

**Risk: SAFE** — markdown edit under `.brain/knowledge/research/`

2026-08-04 digest item #6 (Anti-Fabrication Background Task Notifications) outcome: `confirmed` — this session itself benefits from the notification language (scheduled task preamble explicitly states no live user input). Already marked confirmed in that digest; no change needed.

---

### [SAFE-2] Append Ultraplan removal note to AGENTS.md

**Risk: SAFE** — markdown append to `.brain/AGENTS.md`

`/ultraplan` is removed as of w32. Any CLAUDE.md content, stored prompt, or hook referencing it fails silently. Audit should run before next hook review.

---

### [SAFE-3] Append cross-session messaging and auto-mode notes to AGENTS.md

**Risk: SAFE** — markdown append to `.brain/AGENTS.md`

Two behavioral changes that affect all future sessions:
- Auto mode is now the default permission mode from Aug 14. Sessions starting without explicit mode config now run auto mode, not the prior ask-based default.
- Cross-session messaging + notify_when_idle is now available. The pattern for parallelizing research lanes is now native rather than needing Dynamic Workflows.

---

### [SAFE-4] Add queue items for upgrade work

**Risk: SAFE** — markdown append to `.brain/queue.md`

Add:
- Item 013: Audit CLAUDE.md and stored prompts for `/ultraplan` references (removed in w32)
- Item 014: Evaluate migrating weekly digest to /goal-managed execution with 30-min checkin
- Item 015: Evaluate cross-session messaging for parallel research lanes (replaces sequential WebSearch)

---

### NEEDS APPROVAL

- **settings.json `outputStyle: "Concise"`** — touching settings files requires approval
- **`ANTHROPIC_DEFAULT_MODEL` in environment config** — environment variable changes require approval
- **Auto mode default impact audit** — verifying which hooks or stored prompts assumed `ask` mode behavior; any fixes to hooks require approval
- **Cross-session messaging parallelization of weekly routine** — architectural change to the digest routine; requires approval before modifying the stored prompt

---

## Recommended Actions

1. **Audit for `/ultraplan` references before next cron run.** The command is removed in w32 and fails silently. Check `.claude/hooks/`, CLAUDE.md, stored prompts, and `.brain/routines/` for any reference. Flag for approval if found in hooks.

2. **Prototype `/goal`-managed weekly digest with cross-session messaging lanes.** The combination of `/goal` (persistent completion condition), `notify_when_idle` (event-driven handoff), and `/fork`-with-worktree (isolated parallel branches) is now a complete native replacement for the sequential Ralph Loop pattern. Worth a sandbox test before the next weekly run.

3. **Confirm auto mode behavior in scheduled sessions.** Verify that cron/routine sessions launched after August 14 are actually running auto mode and that no prior explicit `ask` mode config in settings.json is overriding the new default in ways that break permission flow.

---

## Needs Approval

- `settings.json` changes (Concise style, permission mode config)
- `ANTHROPIC_DEFAULT_MODEL` environment variable setup
- Modifying `.brain/routines/weekly-digest-prompt.md` to adopt `/goal` + cross-session messaging pattern
- Hook audit and any fixes for broken `/ultraplan` references or auto-mode assumptions
