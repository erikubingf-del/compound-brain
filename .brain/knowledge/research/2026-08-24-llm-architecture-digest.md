# LLM Architecture Digest: 2026-08-24

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** 4-lane research scan covering Claude Code weeks 30–34 (July 20 – August 21, 2026). Dedup checked against the two prior digests (2026-08-03, 2026-08-04). Items already reported are excluded; two prior findings receive outcome updates where official docs contradict or revise them.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | Cross-Session Messaging | Claude Code sessions on the same machine can now message each other natively. `ListAgents` discovers live sessions; `SendMessage` passes text (never conversation history or files). `@name` in prompt auto-delivers. `notify_when_idle` field gets one notice when a session next goes idle. macOS/Linux since v2.1.224; Windows since v2.1.239. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 2 | Task Tools Removed on Newer Models | TaskCreate, TaskUpdate, TodoWrite, and similar task-tracking tools are **no longer available on Opus 4.8, Sonnet 5, Fable 5, and later models**. Set `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` to re-enable. Affects any skill, hook, or routine that calls these tools in a session running on a newer model. | https://code.claude.com/docs/en/whats-new/2026-w33 | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 3 | Fork Mode On By Default (Full Context Inheritance) | Fork mode is now on by default in interactive sessions. `claude request`s the `fork` subagent type, which inherits the full conversation and prompt cache — no re-explaining context for a side task. `/subtask` triggers it. Turn off with `CLAUDE_CODE_FORK_SUBAGENT=0`. Distinct from prior w29 `/fork` (background copy of session) — this is subagent-level, not session-level. | https://code.claude.com/docs/en/whats-new/2026-w33 | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 4 | Concise Output Style | New built-in `"outputStyle": "Concise"` in settings. Claude leads with the result, skips preamble and narration, still does work as thoroughly as Default. Full detail on explicit ask. Errors, warnings, and destructive-action confirmations keep complete content. Toggle via `/config`. | https://code.claude.com/docs/en/whats-new/2026-w34 | ADOPT — [VERIFIED: official docs w34] | high | pending |
| 5 | /goal 30-Minute Background Check-ins | When background tasks keep a `/goal` waiting, Claude now checks in after 30 minutes and keeps checking at longer intervals while the session is idle, instead of waiting indefinitely. `CLAUDE_CODE_GOAL_CHECKIN_MINUTES=0` to opt out. Directly improves autonomous loop resilience. | https://code.claude.com/docs/en/whats-new/2026-w34 | ADOPT — [VERIFIED: official docs w34] | high | pending |
| 6 | Skills with context:fork Run in Background | Skill frontmatter now supports `context: fork`, which runs the skill in a background subagent by default. `background: false` overrides and waits for the result in the same turn. Enables safe parallelism within a skill without the caller blocking. | https://code.claude.com/docs/en/whats-new/2026-w30 | ADOPT — [VERIFIED: official docs w30] | high | pending |
| 7 | Ultraplan Preview Removed | The `/ultraplan` command and `ultraplan` keyword are removed. Use plan mode or Claude Code on the web instead. Queue items referencing Ultraplan as a planned pattern need updating. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT (info) — [VERIFIED: official docs w32] | high | pending |
| 8 | Background Sessions: Conditional Auto-PR (Revision) | Background sessions now commit and push before finishing **and open a draft PR only when the task calls for one** — not automatically for all code work. Revises the 2026-08-04 digest finding #9 ("Background Agents Auto-PR"), which reported the prior w27 behavior of always auto-opening a draft PR. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT (correction) — [VERIFIED: official docs w32] | high | pending |
| 9 | 200-Subagent Cap Removed (Revision) | The per-session 200-subagent cap introduced in w29 is removed in w32. Long-running sessions no longer refuse new subagents. Concurrency (20 by default; `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`) and depth limits (5 levels) still apply. Revises 2026-08-04 digest finding #7 ("Session-Wide Caps"). | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT (correction) — [VERIFIED: official docs w32] | high | pending |
| 10 | Worktree Isolation Now Blocks Bash + Git Redirects | Worktree isolation now blocks not only file edits but also Bash commands and git redirects that reach the main checkout, in every session type including subagents. Closes a bypass path: a worktree agent could previously run `git -C ..` or a Bash redirect to touch main. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |
| 11 | Auto Mode as Default Permission Mode | Starting August 14, auto mode is the default for new sessions on Pro, Max, and Team plans. A set user default stays unless accepted; org-managed defaults don't change. Classifier calls no longer count toward usage limits. Changes the default permission model for all new brain sessions. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |
| 12 | Claude Security Plugin | Official Anthropic plugin: multi-agent vulnerability scan — agents map architecture, build threat model, hunt findings, independently review each one, write report to `CLAUDE-SECURITY-<timestamp>/`. Scope to whole repo, diff, PR, or commit. Findings → patches you apply yourself. Install from `claude-plugins-official` marketplace. | https://code.claude.com/docs/en/whats-new/2026-w30 | WATCH — [VERIFIED: official docs w30] | high | pending |
| 13 | Claude Opus 5 | New default Opus model. 1M-token context on Anthropic API, Max, Team, Enterprise. Fast mode moves to Opus 5 at $10/$50/MTok. Model ID: `claude-opus-5`. Task-tracking tools unavailable on Opus 5 (see find #2). | https://code.claude.com/docs/en/whats-new/2026-w30 | WATCH — [VERIFIED: official docs w30] | high | pending |
| 14 | Fractal — Multi-Agent Worktree Orchestrator | Community (GitHub trending Aug 2026): orchestrates Claude Code, Codex, and other agents in per-node Git worktrees with recursive delegation and a live TUI. Each agent node gets its own worktree. Pattern: tree-shaped delegation with live visibility. Untrusted — extract pattern only, never install. | https://startupcorners.com/digest/devtools-digest-2026-08-06 | WATCH — [UNVERIFIED: third-party community project; pattern extractable] | medium | pending |
| 15 | Self-Hosted Environments | Run Claude Code cloud sessions on your own infrastructure (Team/Enterprise, public beta). `claude self-hosted-runner` turns machines/containers into runners. Sessions from claude.ai, mobile, desktop, or `claude --cloud` route into your network with access to internal services. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |

---

## Patterns Worth Knowing

### 1. Cross-Session Messaging Changes the Multi-Routine Architecture

Brain routines no longer need file-based coordination signals (`queue.md` claims, lock files, state JSON). A session can now message another running session directly using `SendMessage` after discovering it with `ListAgents`. For compound-brain: a digest routine can notify a monitoring session of a new queue item; a research lane can report back to the orchestrating session; a cron-triggered session can hand off to an attended session. The `notify_when_idle` flag is a clean replacement for polling: rather than sleeping until another session finishes, a session registers interest and wakes on idle. File-based queue still useful for persistence across session boundaries; session messaging useful within a concurrent run.

### 2. Task Tools Are Gone on Newer Models — Audit Before Upgrading

`TaskCreate`, `TaskUpdate`, `TodoWrite` are removed on Opus 4.8, Sonnet 5, Fable 5, and later. Any routine, skill, or hook that calls these tools will silently fail (or error) when the session runs on a newer model. The workaround (`CLAUDE_CODE_ENABLE_TODO_TOOLS=1`) can be set in the session environment or startup hook, but it is an explicit opt-in — it will not be set by default. This brain's own scheduled routines should audit for implicit dependency on these tools, particularly any compound skill that chains into a task-writing step.

### 3. Fork Mode + Context Inheritance Replaces "Re-Explain" Patterns

With fork mode on by default, any subagent spawned in an interactive session inherits the full conversation and prompt cache. Prior pattern: pass full context in the subagent prompt because the subagent starts fresh. New pattern: spawn with `/subtask` or `fork` type and the subagent already knows everything the parent knows. Significant for research lane parallelism: each research lane can start knowing the prior digest contents without a re-paste in the prompt.

### 4. Concise Output Style + /goal Check-ins = Quieter Autonomous Sessions

Two independent settings that compose well for autonomous loops: `"outputStyle": "Concise"` removes narration from routine output, and `/goal` with 30-minute background check-ins prevents indefinite waits without flooding a session with constant pings. For a weekly digest routine: set Concise in the settings file for less verbose commit message output; use `/goal` to wrap long research tasks so the session checks in if a WebSearch stalls.

### 5. Worktree Isolation Now Fully Enforced

Previously, worktree isolation blocked file edits to the main checkout but a worktree agent could still reach it via Bash (`git -C ../..`) or redirection. w32 closes this. Implication: existing brain agents that run in worktrees and intentionally write to the main checkout (e.g., a subagent committing to `.brain/` in the parent) will now be blocked. The correct pattern is: write in the worktree and open a PR, or run the agent in the main checkout directly, not in a worktree.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| Cross-session messaging | Routine coordination | Replace file-lock queue claims with `SendMessage`; use `notify_when_idle` instead of polling loops |
| Concise output style | All scheduled routines | Less verbose output in unattended sessions; set in `.claude/settings.json` or session start hook |
| context:fork skill frontmatter | Candidate skills | Mark parallelizable skills (research lanes, code scans) to run in background without caller changes |
| /goal check-ins for digest run | Weekly digest routine | Wrap the 4-lane search in a `/goal` so the session checks in after 30 min if a lane stalls |
| CLAUDE_CODE_ENABLE_TODO_TOOLS | Session-start hook | Add to the hook env if any resident skill depends on task tools; otherwise audit and remove those calls |
| Auto mode default | Brain permission setup | Once auto mode is the system default, the "permission setup session" recommendation becomes: verify auto mode is active, not approve individual tools |
| Ultraplan references | queue.md / AGENTS.md | queue items 002/008 referenced Ultraplan; now removed — update to "plan mode" |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Update Prior Digest Outcome Fields

**Risk: SAFE** — markdown edits under `.brain/knowledge/research/`

Two findings from 2026-08-04 are materially revised by official docs:

- **Finding #7** (Session-Wide Caps for WebSearch and Subagents): The 200-subagent cap was removed in v2.1.224 (w32). Update outcome from `pending` → `REVISED — 200-subagent cap removed w32; WebSearch (200/session) and concurrency (20 concurrent) limits still apply`.
- **Finding #9** (Background Agents Auto-PR): Behavior changed in w32. Update outcome from `pending` → `REVISED — w32 changes to "open draft PR only when task calls for one", not on all code work`.

---

### [SAFE-2] Add AGENTS.md Learnings

**Risk: SAFE** — append to `.brain/AGENTS.md`

Add this run's 3 learnings:
1. Task tools (TaskCreate, TaskUpdate, TodoWrite) removed on Opus 5 / Sonnet 5 / Fable 5 and later — check CLAUDE_CODE_ENABLE_TODO_TOOLS=1 if any skill depends on them; never assume they are available.
2. Cross-session messaging (`ListAgents` + `SendMessage` + `@name`) is now a native primitive — prefer it over file-based coordination for same-machine concurrent sessions.
3. Worktree isolation now blocks Bash + git redirects to main checkout; worktree agents that intentionally committed to the parent tree must be redesigned.

---

### [SAFE-3] Update queue.md

**Risk: SAFE** — markdown edits to `.brain/queue.md`

Changes:
- Close the current run row (add row 012 for this run, mark in_progress → done).
- Row 003 (Ultraplan reference in queue 005): note `/ultraplan` removed; see plan mode.
- Add row 012: Audit candidate-skills/ for `context: fork` opportunities — mark parallelizable skills (SAFE, draft only).
- Add row 013: Verify task-tool dependency in scheduled routines; add `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` to session environment if needed — NEEDS APPROVAL (hooks/settings).
- Add row 014: Design cross-session messaging coordination for digest routine's research lanes (SAFE, draft spec under `.brain/knowledge/resources/`).

---

### [SAFE-4] Draft context:fork Candidate Skill Note

**Risk: SAFE** — new file under `.brain/candidate-skills/`

Skill opportunity: a `parallel-research-lanes` skill wrapper that marks itself `context: fork` so each lane runs as a background subagent inheriting the full session context. Useful for replacing the digest routine's sequential 4-lane WebSearch with a parallel fan-out. Draft a SKILL.md stub in `.brain/candidate-skills/parallel-research-lanes/`.

---

## Recommended Actions

1. **Audit all routines and skills for task-tool dependency immediately.** `TaskCreate`, `TaskUpdate`, `TodoWrite` silently disappear on Opus 5 / Sonnet 5 / Fable 5. A routine that calls these on a newer model gets no error message — just no task created. Add `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` to the session environment in the start hook (needs approval) or remove the dependency from routines. Do this before any session upgrade to a newer model.

2. **Prototype cross-session messaging as a coordination primitive.** `ListAgents` + `SendMessage` now replace the file-lock queue claim pattern for same-machine concurrent sessions. The digest routine's 4 research lanes could each run in a fork subagent, messaging back findings as they complete, with the parent synthesizing. Draft the coordination spec under `.brain/knowledge/resources/` (SAFE). Implementation needs approval for hook/settings changes.

3. **Set `"outputStyle": "Concise"` in the session environment for unattended runs.** Autonomous sessions produce cleaner commit diffs and shorter logs with Concise mode. This is a `.claude/settings.json` change (needs approval for settings), but the value of doing it is clear and the risk is low.

---

## Needs Approval

- **Add `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` to session-start hook or settings** — hooks/settings require approval; without it any task-tool calls silently fail on Opus 5+
- **Set `"outputStyle": "Concise"` in `.claude/settings.json`** — settings change requires approval
- **Verify auto mode is active for scheduled sessions** — permission mode change requires approval
- **Promote parallel-research-lanes draft to `.claude/skills/` or `plugins/`** — execution context requires approval
- **Design and deploy cross-session messaging coordination for digest lanes** — implementation touches hooks/session config; draft is SAFE, wiring is not
