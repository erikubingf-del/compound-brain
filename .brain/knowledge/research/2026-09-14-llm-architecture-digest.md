# LLM Architecture Digest: 2026-09-14

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** 4-lane research scan covering official Claude Code docs (weeks 30–34,
post-2026-08-04), community patterns, and recent arxiv memory research. Prior
digests already covered weeks 27–29; those findings are not re-reported here.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | Cross-Session Messaging | Sessions on the same machine discover each other with `ListAgents` and pass text with `SendMessage`; `@session-name` in the prompt is the shortcut. Windows support added in w34. Native multi-session coordination without a broker. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32/w34] | high | pending |
| 2 | Fork Mode Default + `/subtask` Inherits Context | Fork mode on by default in interactive sessions (v2.1.232). `/subtask` spawns a fork subagent that inherits the full conversation and prompt cache — no re-explanation of context needed. Disable with `CLAUDE_CODE_FORK_SUBAGENT=0`. | https://code.claude.com/docs/en/whats-new/2026-w33 | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 3 | Concise Output Style | New built-in output style (`outputStyle: "Concise"` in settings). Claude leads with the result and skips preamble; works with explicit "explain more" requests; safety/error output always complete. Directly useful in unattended routine sessions. | https://code.claude.com/docs/en/whats-new/2026-w34 | ADOPT — [VERIFIED: official docs w34] | high | pending |
| 4 | Skills with `context: fork` | A skill's frontmatter can declare `context: fork` so it runs in a background fork subagent by default; `background: false` waits for the result in-turn. Changes skill authoring pattern for research or long-running tasks. | https://code.claude.com/docs/en/whats-new/2026-w30 | ADOPT — [VERIFIED: official docs w30] | high | pending |
| 5 | `notify_when_idle` on SendMessage | Pass `notify_when_idle` when messaging another session, and it sends one notice back when it next goes idle. Low-overhead orchestration primitive: fire a session, get pinged when it's done, without polling. | https://code.claude.com/docs/en/whats-new/2026-w34 | ADOPT — [VERIFIED: official docs w34] | high | pending |
| 6 | /code-review Runs as Background Subagent | `/code-review` now runs in its own context window so review work stays out of the main conversation. Findings arrive when complete. All effort levels (high, xhigh, max) run this way since w33. | https://code.claude.com/docs/en/whats-new/2026-w30 | ADOPT — [VERIFIED: official docs w30/w33] | high | pending |
| 7 | Task Tools Disabled on Newer Models | `TaskCreate`, `TaskUpdate`, `TodoWrite` (and the full task-tracking suite) are no longer available on Sonnet 5, Fable 5, Mythos 5, and later. Re-enable with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`. Silent change — routines that relied on these silently no-op on new models. | https://code.claude.com/docs/en/whats-new/2026-w33 | WATCH — [VERIFIED: official docs w33] | high | pending |
| 8 | 200-Subagent Cap Removed | The 200-subagent-per-session cap is removed (v2.1.224). Concurrency limit (20 concurrent by default, tunable via `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`) and depth (5 levels) still apply. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |
| 9 | Auto Mode Now Default | Auto mode became the default permission mode for Pro/Max/Team plans starting August 14 (v2.1.224). Classifier calls no longer count toward usage limits. Existing `defaultMode` settings are preserved. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |
| 10 | Claude Opus 5 | New default Opus model replacing Opus 4.8: 1M-token context window, fast mode at $10/$50 per MTok. Available on Max, Team Premium, Enterprise pay-as-you-go, Anthropic API, and cloud platforms. | https://code.claude.com/docs/en/whats-new/2026-w30 | WATCH — [VERIFIED: official docs w30] | high | pending |
| 11 | Claude Security Plugin | Official Anthropic plugin: multi-agent vulnerability scan — architecture map, threat model, findings, independent review — writes to `CLAUDE-SECURITY-<timestamp>/`. Scan whole repo, diff, PR, or commit. Produces reviewed patches you apply yourself. | https://code.claude.com/docs/en/whats-new/2026-w30 | WATCH — [VERIFIED: official docs w30] | high | pending |
| 12 | GitLab MR Worktree Support | `claude --worktree <gitlab-MR-url>` branches from a merge request (v2.1.233+). `claude agents` labels sessions `!N`. Plugin marketplaces clone bare `gitlab.com` URLs including nested subgroups. GitLab token families redacted. | https://code.claude.com/docs/en/whats-new/2026-w33 | WATCH — [VERIFIED: official docs w33] | high | pending |
| 13 | Memory in the Loop (arxiv 2607.05690) | In-process retrieval as extended working memory for LLM agents: argues that retrieval latency (up to 83×) is a property of *where* the store lives, not of in-loop retrieval itself. In-process stores (embedded, not networked) close the gap. | https://arxiv.org/abs/2607.05690 | TEST — [UNVERIFIED: arxiv blocked, summary from search results only; do not implement until paper read] | medium | pending |
| 14 | Always-On Agents Governance Survey (arxiv 2606.30306) | Survey of persistent memory, state, and governance patterns for long-running LLM agents. Covers lifecycle management (write–manage–read loop), tail-latency handling, and governance mechanisms for autonomous agents. | https://arxiv.org/abs/2606.30306 | TEST — [UNVERIFIED: arxiv blocked, summary from search results only; do not implement until paper read] | medium | pending |

---

## Patterns Worth Knowing

### 1. Cross-Session Messaging as a Zero-Broker Orchestration Bus

`ListAgents` + `SendMessage` + `@` mentions give Claude Code a native inter-session
bus with no external broker. The pattern for brain routines: launch a research
fork, have it signal completion or a finding via `SendMessage` to the parent
session, parent resumes with `notify_when_idle`. This replaces polling and
arbitrary sleep intervals with an event-driven idle notification. Combined with
fork mode (inherits full context), subagents can be spawned cheaply for parallel
research without the overhead of re-explaining state.

### 2. Fork Mode Redefines the Subagent Cost Model

Before w33, spawning a subagent meant a fresh context window and re-explanation
overhead. With fork mode default, `/subtask` hands the full conversation to the
fork. The practical change: tasks that previously needed a long system prompt or
a handoff document now need neither. For compound-brain, this means the weekly
digest routine can fork research lanes mid-run without a bootstrapping prompt
per lane.

### 3. The Task-Tools Removal Is a Silent Breaking Change for Routines

`TaskCreate`, `TaskUpdate`, and `TodoWrite` were the harness-tracked task tools.
They are disabled by default on all models from Sonnet 5 forward. Any routine
(including this digest) that was counting on task-tool tracking silently no-ops
on those models. The fix is either `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` (re-enables
the tools) or switching to native queue-based tracking (`.brain/queue.md`) which
this brain already does. The silent nature is the risk: there is no error, just
absent functionality.

### 4. In-Process Memory Retrieval: Latency Is Architectural, Not Inherent

The "Memory in the Loop" paper (arxiv 2607.05690) argues that the 83× latency
overhead of in-loop retrieval is caused by networked vector stores (~200ms per
call), not by retrieval inside the loop itself. An in-process store (same
process, no network hop) brings latency down to the point where per-step
retrieval becomes viable. For brain: the SAGE novelty-gate prototype (queue 005)
could pair with an in-process retrieval layer rather than relying on a vector
database, keeping the read cost near-zero.

### 5. Auto Mode as the New Permission Baseline

Auto mode is now the default for Pro/Max/Team. This changes the mental model for
unattended routines: instead of "what permissions do I need to approve?", the
question is "what does the auto-mode classifier allow by default, and what hard
deny rules do I need?". For brain cron sessions, the prior strategy of
pre-approving permissions in a setup session (noted in the 08-04 digest) still
holds, but the auto-mode classifier is now the first line of defense rather than
a research preview.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| Cross-session messaging + `notify_when_idle` | Weekly digest routine | Parallel research lanes without polling; each lane sends `SendMessage` on completion; parent session resumes idle-aware |
| Fork mode for research lanes | Weekly digest routine | Each research lane forked mid-run inherits full context; no per-lane bootstrapping prompt needed; reduces routine complexity |
| Concise output style | All unattended routines | Shorter transcripts; results surfaced faster; errors and warnings still complete |
| Skills with `context: fork` | Brain skills (brain-digest, brain-orient) | Long-running skills run in background automatically; main session stays responsive |
| CLAUDE_CODE_ENABLE_TODO_TOOLS=1 audit | All routines using task tools | Determine if any routine relied on task tools; either enable them explicitly or confirm queue.md is the sole tracking mechanism |
| Always-On Agents governance patterns | .brain/state/ runtime model | Survey covers write–manage–read loop and tail-latency governance; relevant to SAGE prototype and runtime-governor design |
| In-process retrieval pattern | SAGE novelty gate (queue 005) | Pair novelty gate with in-process store; removes the need for a networked vector database |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Update Prior Digest Outcome Fields

**Risk: SAFE** — markdown edit under `.brain/knowledge/research/`

Item 6 from 2026-08-04 (Anti-Fabrication Notifications) is confirmed — this
session's scheduled-task envelope includes the anti-fabrication language explicitly.
No other ADOPT items from prior digests have been confirmed or invalidated this
run; they remain `pending`.

Applied below: the 2026-08-04 digest entry for item 6 already shows
`outcome: confirmed`. No further edits needed to prior digest files this run.

---

### [SAFE-2] Note Task-Tools Removal in AGENTS.md

**Risk: SAFE** — append to `.brain/AGENTS.md`

`TaskCreate`/`TaskUpdate`/`TodoWrite` disabled on Sonnet 5+ by default
(`CLAUDE_CODE_ENABLE_TODO_TOOLS=1` re-enables). Silent break — no error on newer
models, the tools simply don't exist. Brain routines that use task tools need to
set the env var or confirm they only use `.brain/queue.md`. Applied in Step 5.

---

### [SAFE-3] Add Queue Items for New Opportunities

**Risk: SAFE** — append to `.brain/queue.md`

New tasks worth queuing:
- Audit routines for task-tool usage (SAFE to investigate)
- Evaluate Concise output style for unattended routines (SAFE)
- Review Always-On Agents governance paper when arxiv access available

Applied in Step 5.

---

### NEEDS APPROVAL (list only — never applied here)

- **Enable `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` in settings** — modifying settings files requires approval
- **Claude Security plugin install and scan** — `claude-security@claude-plugins-official` install + `/claude-security` scan is a multi-agent code scan; requires approval before running
- **Cross-session messaging in hooks or scripts** — using `SendMessage`/`ListAgents` programmatically from hooks requires hook changes (NEEDS APPROVAL)
- **Read Always-On Agents and Memory-in-the-Loop papers** — arxiv is blocked by egress proxy; requires unblocking or alternative access

---

## Recommended Actions

1. **Verify task-tool usage across routines.** Run `grep -r "TaskCreate\|TaskUpdate\|TodoWrite" .brain/` to find any references. If any exist, either add `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` to the environment or confirm `.brain/queue.md` fully covers that tracking need. This is SAFE to investigate; the setting change needs approval.

2. **Set `outputStyle: "Concise"` for unattended routines.** The Concise output style is well-suited to scheduled runs: shorter transcripts, results first, safety content still complete. Configure via `"outputStyle": "Concise"` in settings (needs approval) or document it as a recommended per-session config for routine prompts.

3. **Design a fork-based parallel research lane pattern.** Fork mode is now default and inherits full context. The weekly digest routine could fork 4 research lanes simultaneously (one per lane in Step 1), each returning findings via `SendMessage`, instead of sequential WebSearch calls. This is a routine-prompt change (SAFE) paired with a hook/settings change for cross-session messaging (NEEDS APPROVAL).
