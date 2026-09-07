# LLM Architecture Digest: 2026-09-07

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** Full 4-lane research scan. Covers official docs w30–w34 (July 20 – August 21, 2026) plus
community/third-party findings. Digests through 2026-08-04 are on record; nothing prior to w30 is
re-reported. Branch pushed: `claude/cool-heisenberg-bity3f` (session constraint; default is `main`).

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | Cross-Session Messaging | Claude Code sessions discover each other with `ListAgents` and exchange short text messages with `SendMessage`. macOS, Linux, Windows. Throttled to prevent message loops. A coordination primitive for multi-session brain orchestration. | https://code.claude.com/docs/en/cross-session-messaging | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 2 | TaskCreate/TaskUpdate Unavailable on Sonnet 5+ | Task-tracking tools (`TaskCreate`, `TaskUpdate`, `TodoWrite`) disabled by default on Sonnet 5, Fable 5, Mythos 5, and later. Re-enable with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`. Breaking change for any routine or hook using these on newer models. | https://code.claude.com/docs/en/tools-reference#task-tool-availability | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 3 | Fork Mode On by Default (Interactive Sessions) | Subagents spawned by `fork` type inherit the full conversation and prompt cache. No more re-explaining context to a subtask agent. Default in interactive sessions; opt out with `CLAUDE_CODE_FORK_SUBAGENT=0`. | https://code.claude.com/docs/en/sub-agents#turn-fork-mode-on-or-off | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 4 | 200-Subagent Cap Removed | The 200-subagent-per-session hard cap is gone (was reported as a WATCH item in 2026-08-04 digest). Concurrency and depth limits still apply. Long-running sessions can now spawn subagents without hitting a session wall. | https://code.claude.com/docs/en/sub-agents#concurrent-subagent-limit | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 5 | notify_when_idle on SendMessage | New input on `SendMessage`: pass `notify_when_idle` and the target session sends one notice back when it goes idle. Single-message coordination without polling. Useful for chaining brain routines. | https://code.claude.com/docs/en/cross-session-messaging#get-a-notice-when-another-session-goes-idle | ADOPT — [VERIFIED: official docs w34] | high | pending |
| 6 | Worktree Isolation Blocks Bash + git Cross-Reads | Worktree isolation now blocks Bash commands and git redirects that reach the main checkout, not just file edits. Applies to every session type including subagents. Potential silent breakage for hooks/scripts that assume cross-worktree shell access. | https://code.claude.com/docs/en/worktrees#how-claude-code-enforces-isolation | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 7 | Concise Output Style | Built-in output style: Claude leads with the result, skips preamble and narration, does full work anyway. Set `"outputStyle": "Concise"` in `settings.json`. Error reports and destructive confirmations stay complete. Ideal for automated brain routines. | https://code.claude.com/docs/en/output-styles#built-in-output-styles | ADOPT — [VERIFIED: official docs w34] | high | pending |
| 8 | Auto Mode Now Default (Aug 14) | Auto mode became the default permission mode for new sessions on Pro, Max, and Team as of August 14, 2026. Classifier-based; runs safe actions without prompts. Already-set defaults remain unless user accepts the switch prompt. Affects session startup behavior in cloud/scheduled runs. | https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 9 | Skills with `context: fork` Run Background by Default | Skills declaring `context: fork` in frontmatter now run as background subagents by default. Set `background: false` to wait in same turn. Changes the execution model for compound-brain plugin skills. | https://code.claude.com/docs/en/skills#run-skills-in-a-subagent | ADOPT — [VERIFIED: official docs w30] | high | pending |
| 10 | Self-Hosted Environments | Run Claude Code cloud sessions on org-owned infrastructure. `claude self-hosted-runner` turns a machine into a runner. Sessions started from claude.ai run inside the org network with access to internal services. Public beta, Team/Enterprise. | https://code.claude.com/docs/en/self-hosted-environments-quickstart | WATCH — [VERIFIED: official docs w32] | high | pending |
| 11 | Claude Security Plugin | Official Anthropic plugin: multi-agent vulnerability scan — agents map architecture, build threat model, hunt vulns, peer-review findings, write report to `CLAUDE-SECURITY-<timestamp>/`. Scan whole repo or diff/PR/commit. Findings become reviewed patches you apply yourself. Pattern is extractable. | https://code.claude.com/docs/en/claude-security#scan-and-fix-your-codebase | WATCH — [VERIFIED: official docs w30] | high | pending |
| 12 | Fractal — Hierarchical Agent Loops | Third-party: agents organize into trees, each node iterates in a git worktree and spawns children for separable subtasks. Hard caps on iterations, cost, time, descendants. SQLite state. Multi-backend (Claude Code, Codex, Grok). Pattern is extractable; do NOT install. | https://github.com/plasma-ai/fractal | WATCH — [UNVERIFIED: third-party; patterns extractable but no install] | medium | pending |
| 13 | Cognitive 5-Type Memory Model (2026 Survey) | Academic survey maps agent memory systems through a cognitive lens: working memory (context window), episodic (event store), semantic (knowledge graph), procedural (skill/code), and prospective (scheduled intent). Framework aligns with the .brain/ tiered architecture. | https://arxiv.org/html/2603.07670v1 | WATCH — [UNVERIFIED: academic paper; informational only] | medium | pending |
| 14 | /ultraplan Removed | `/ultraplan` command and `ultraplan` keyword are removed in w32. Use plan mode or Claude Code on the web instead. Prior digest (2026-08-03 item 3) classified Spec-Driven Development / UltraPlan as ADOPT — this removes the native CLI surface but not the spec-first pattern itself. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 15 | /design Skill (Research Preview) | Brings Claude Design's artboard workflow to CLI and Desktop. Publishes editable canvas of UI artboards as an artifact; pick one, tweak, then have Claude implement it. Built on artifacts. Pro/Max/Team/Enterprise. Requires v2.1.234+. | https://code.claude.com/docs/en/artifacts#availability | WATCH — [VERIFIED: official docs w34] | high | pending |

---

## Patterns Worth Knowing

### 1. Session Mesh: Cross-Session Messaging as Orchestration Fabric

Cross-session messaging (w32/w34) enables a new architectural pattern: sessions on the same machine
(or in the same cloud environment) form a mesh rather than a monolith. An orchestrator session
discovers workers with `ListAgents`, delegates via `SendMessage`, and coordinates completion with
`notify_when_idle`. Combined with fork mode (w33) — which gives subtask agents full parent context
— this enables lightweight multi-brain coordination without a separate broker process. The throttle
on repeated messages prevents loop spirals. For compound-brain: a coordinator session could dispatch
research lanes to worker sessions while continuing its own work, then collect results when workers
go idle.

### 2. Fork Mode as Default Changes the Agent Mental Model

Fork mode on by default (w33) means the default subagent is no longer a clean-slate worker — it is
a context-inheriting collaborator. The old pattern (spawn subagent, re-explain context) is now the
exception. This changes how compound-brain skills should be designed: skills that previously wrote
long context-setting preambles can now rely on the parent conversation being present. The tradeoff:
context inheritance is expensive in tokens; set `context: none` explicitly for skills where a clean
slate is preferable (e.g. isolated research scanners).

### 3. Fractal's Hard-Cap Architecture: Bounding Recursive Delegation

Fractal's contribution is not the tree structure itself but the hard caps enforced at each node:
max iterations, max cost, max time, max children, max descendants. These caps are set per node and
inherited by children unless overridden. This prevents the common failure mode of recursive agent
systems — unbounded spending spirals when subtasks spawn more subtasks than expected. The pattern
is directly applicable to compound-brain: any autonomous routine that can spawn sub-routines needs
inherited cost/iteration caps, not just a global session cap.

### 4. Breaking Change Accumulation: w30–w34 Has Several

Three w30–w34 items are silent-failure risks for compound-brain routines:
- **TaskCreate/TaskUpdate gone on Sonnet 5+**: any routine that calls these tools on newer models
  silently loses task tracking. The tool calls succeed but do nothing (or error).
- **Worktree Bash isolation expanded**: hooks or scripts that reach across worktree boundaries via
  shell now fail. This was file-only before.
- **PreToolUse auto-allow hooks no longer bypass internal side tasks**: summaries and compaction
  bypass is closed (w32 "Other wins"). If any compound-brain hook used auto-allow to speed up
  internal summaries, it is now ignored in that context.

### 5. Cognitive Memory Taxonomy as .brain/ Design Frame

The 2026 cognitive survey's five memory types (working/episodic/semantic/procedural/prospective)
map directly onto the .brain/ layout: MEMORY.md = episodic trace; knowledge/ = semantic store;
candidate-skills/ = procedural; routines/ = prospective (scheduled intent); active context window
= working memory. The survey's benchmark suite (LoCoMo, LongMemEval, BEAM) could serve as a
future self-evaluation framework for compound-brain's memory quality. No code to run — pure design
reference.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| Cross-session messaging | Research routine | Dispatch 4 search lanes to worker sessions simultaneously; collect on `notify_when_idle`; main session synthesizes |
| Fork mode awareness | All plugin skills | Skills relying on context inheritance now get it by default; refactor context-preamble blocks in skills where clean slate is better |
| notify_when_idle | Queue coordination | A brain orchestrator session can dispatch tasks and get woken when each completes without polling |
| Concise output style | Automated routines | Set `outputStyle: Concise` in cloud session settings to reduce token waste in routine text output |
| TaskCreate/TaskUpdate deprecation | All routines on Sonnet 5+ | Audit whether any routine or hook calls these tools; either set `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` or remove the calls |
| Worktree Bash isolation | Hooks + scripts | Audit `.claude/hooks/` for any shell commands that cross worktree boundaries; these now silently fail |
| Hard-cap pattern from Fractal | Autonomous routines | Add per-routine cost/iteration caps to the routine spec in .brain/routines/; prevents unbounded recursion |
| Cognitive 5-type framework | .brain/ architecture | Use as a design check: does each memory tier map to a cognitive type? Identify gaps (prospective memory in particular) |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Update Prior Digest Outcome Field — 200-Subagent Cap Removed

**Risk: SAFE** — markdown edit under `.brain/`

In the 2026-08-04 digest, item 7 "Session-Wide Caps for WebSearch and Subagents" was classified
WATCH with outcome `pending`. The 200-subagent-per-session cap was removed in w32 (August 3–7,
2026). Update that item's outcome to `invalidated — subagent cap removed in w32; WebSearch cap
status unknown, treat as still active until verified`.

Append a note under item 7 in the 2026-08-04 digest.

---

### [SAFE-2] Add Queue Items for Breaking Changes

**Risk: SAFE** — markdown append to `.brain/queue.md`

Add:
- Item 013: Audit routines/hooks for `TaskCreate`/`TaskUpdate` calls — these are disabled on
  Sonnet 5+ by default. Check all routines and remove or gate behind env var. Priority: high.
- Item 014: Audit `.claude/hooks/` for cross-worktree Bash commands — now blocked by worktree
  isolation. Priority: medium.
- Item 015: Add cost/iteration cap fields to `.brain/routines/weekly-digest-prompt.md` — adopt
  the Fractal hard-cap pattern for bounded recursion. Priority: low.

---

### [SAFE-3] Append Learnings to AGENTS.md

**Risk: SAFE** — append to `.brain/AGENTS.md`

Append this run's 3 learnings (done as part of Step 5 below).

---

### [SAFE-4] Draft Candidate Skill: Session Coordinator

**Risk: SAFE** — write `.brain/candidate-skills/session-coordinator/SKILL.md`

The cross-session messaging primitives (`ListAgents`/`SendMessage`/`notify_when_idle`) enable a
repeatable coordination pattern: an orchestrator discovers workers, dispatches tasks, and awaits
idle signals. This is a bounded, documented capability suitable for a skill draft.

Draft contents:
- Purpose: discover live sessions, send task instructions, await `notify_when_idle` completion signals
- Inputs: task description, target session name (or `auto` for first available idle session)
- Output: task acknowledgment and idle notification
- Safety: only text messages; no file sharing; loop throttle is enforced by Claude Code itself
- Draft only; human promotes to `.claude/skills/` or `plugins/`

---

## Recommended Actions

1. **Audit for TaskCreate/TaskUpdate before next scheduled run.** The deprecation on Sonnet 5+
   defaults is a silent failure — tools appear available in docs but do nothing on newer models.
   Check `.brain/routines/` and any hooks that call these tools. Set `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`
   in cloud session config or remove the calls. This is queue item 013.

2. **Set `outputStyle: Concise` in cloud session settings for brain routines.** Automated brain
   sessions produce verbose text output that consumes tokens without adding value to the written
   state. The Concise style preserves full work quality while skipping preamble and narration.
   Needs approval to touch settings files.

3. **Evaluate cross-session messaging for the weekly digest.** The current digest routine runs
   4 search lanes sequentially. With cross-session messaging + `notify_when_idle`, each lane can
   run in a parallel worker session. Wall-clock time drops proportionally. Pattern: orchestrator
   dispatches, workers search and report, orchestrator synthesizes on idle signals. Draft a
   candidate skill for this pattern (SAFE-4 above).

---

## Needs Approval

- **`outputStyle: Concise` in settings** — modifying `.claude/settings.json` or cloud session settings requires approval
- **`CLAUDE_CODE_ENABLE_TODO_TOOLS=1` in cloud config** — environment variable change in session config requires approval
- **Hook audit and fixes** (queue 014) — touching `.claude/hooks/` requires approval
- **Promoting candidate skill to active skill** — writing to `plugins/` or `.claude/skills/` requires approval; candidate draft under `.brain/` is SAFE
- **Self-hosted environments evaluation** — standing up a runner involves `claude self-hosted-runner setup` and admin-settings changes; Owner action required
