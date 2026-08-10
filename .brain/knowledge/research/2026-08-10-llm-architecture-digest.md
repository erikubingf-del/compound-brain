# LLM Architecture Digest: 2026-08-10

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** 4-lane scan (GitHub trending, Claude Code ecosystem, community techniques,
official docs). Weeks 30–31 returned 404 — most recent official week remains w29 (July 13–17).
This digest covers native features from w24–w26 not reported in prior runs, plus novel community
patterns not previously found. All w27–w29 findings and prior community items (Ralph Loop, SAGE,
DeerFlow, Agno, Hybrid Graph Memory, etc.) are excluded per dedup rule.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | Sub-agents spawn sub-agents (5-level tree) | Subagents can now spawn their own subagents up to 5 levels deep; `/agents` shows the full nested tree with descendant counts and path back to main. Hard cap prevents runaway concurrent chains. | https://code.claude.com/docs/en/sub-agents#let-subagents-spawn-their-own-subagents | ADOPT — [VERIFIED: official docs w24] | high | pending |
| 2 | `--safe-mode` / `CLAUDE_CODE_SAFE_MODE` | Launches with ALL customizations disabled (CLAUDE.md, skills, plugins, hooks, MCP, custom commands). Auth, model selection, and built-in tools still work. If a problem disappears in safe mode, one of those surfaces is the cause. | https://code.claude.com/docs/en/debug-your-config#test-against-a-clean-configuration | ADOPT — [VERIFIED: official docs w24] | high | pending |
| 3 | Agent messaging authority hardening | Messages relayed via `SendMessage` from other agents NO LONGER carry user authority; auto mode blocks them. Prevents a rogue subagent from escalating its own permissions by relaying a message that looks like it came from the user. | https://code.claude.com/docs/en/changelog#2-1-166 | ADOPT — [VERIFIED: official docs w24] | high | pending |
| 4 | `Tool(param:value)` deny/ask rules | Deny and ask rules can now match on tool parameters, e.g. `Agent(model:opus)` blocks only opus-model subagent spawns while allowing others. Enables surgical permission gates without blanket denies. | https://code.claude.com/docs/en/whats-new/2026-w25 | ADOPT — [VERIFIED: official docs w25] | high | pending |
| 5 | Background subagents surface permission prompts | Background subagents now send permission prompts to the main session instead of auto-denying. Dialog shows which agent is asking; Esc denies only that tool. Unblocks autonomous routines that need occasional human approval without requiring foreground execution. | https://code.claude.com/docs/en/whats-new/2026-w26 | ADOPT — [VERIFIED: official docs w26] | high | pending |
| 6 | `sandbox.credentials` setting | Blocks sandboxed commands from reading credential files and secret environment variables. Opt-in hardening for compound-brain sessions that run third-party patterns in a sandbox context. | https://code.claude.com/docs/en/whats-new/2026-w26 | ADOPT — [VERIFIED: official docs w26] | high | pending |
| 7 | `claude mcp login/logout` shell auth | Authenticates a configured MCP server from the CLI via OAuth without opening an interactive session. Enables pre-authenticating MCP servers in a setup step before cron/scheduled runs start. | https://code.claude.com/docs/en/mcp#authenticate-from-the-command-line | ADOPT — [VERIFIED: official docs w26] | high | pending |
| 8 | `fallbackModel` chain | Configures up to 3 fallback models tried in order when primary is overloaded or unavailable. Applies to interactive sessions with `--fallback-model`. Useful for autonomous routines that must not stall on provider outages. | https://code.claude.com/docs/en/model-config#fallback-model-chains | WATCH — [VERIFIED: official docs w24] | high | pending |
| 9 | `disableBundledSkills` setting | Hides built-in skills, workflows, and commands from the model. Useful for creating lean, minimal sessions where only explicitly loaded skills are visible — reduces context noise in focused cron runs. | https://code.claude.com/docs/en/whats-new/2026-w24 | WATCH — [VERIFIED: official docs w24] | medium | pending |
| 10 | `/ultrareview` cloud bug-hunting fleet | Launches a fleet of parallel cloud agents to review a branch from multiple angles (logic, edge cases, security, perf). Each finding is independently verified before surfacing. Research preview; typical cost $5–$20 per run. | https://code.claude.com/docs/en/whats-new/2026-w17 | WATCH — [VERIFIED: official docs w17] | high | pending |
| 11 | Ultraplan cloud planning | Offloads deep planning to a cloud container; plan reviewed in browser via PR-style interface; run remotely or pulled back local. Consumes ~33% of a 5-hour session quota per full plan. | https://code.claude.com/docs/en/whats-new/2026-w15 | WATCH — [VERIFIED: official docs w15] | high | pending |
| 12 | ccswarm: Sangha Consensus + quality gates | Third-party: declarative YAML workflow engine where multiple agents evaluate the same decision independently and must reach consensus before progressing through plan → review → implement → PR stages. NDJSON audit trail supports replay and rollback. | https://github.com/nwiizo/ccswarm | TEST — [UNVERIFIED: third-party; extract consensus pattern, do not install] | medium | pending |
| 13 | Git-native memory layer (pure bash) | Third-party pattern: session memory stored in git notes or a plain markdown graph with ~3ms/event write overhead; zero dependencies, zero services; survives branches; stays local unless explicitly pushed. Directly implementable as a `.brain/` extension. | https://github.com/mourad-ghafiri/git-notes-memory | TEST — [UNVERIFIED: third-party; pattern extractable] | medium | pending |
| 14 | Simmer: judge-loop artifact refinement | Third-party pattern: iterative output refinement using judge subagents that score the artifact against user-defined criteria across multiple rounds, stopping when score threshold is met. Native reimplementation possible using existing subagent + `/goal` primitives. | https://github.com/rohitg00/awesome-claude-code-toolkit | TEST — [UNVERIFIED: third-party; pattern extractable] | medium | pending |
| 15 | Codegraph: pre-indexed code knowledge graph | Third-party: pre-computes full dependency graph at index time; agents query it rather than re-scanning. Auto-reindexes after commits via PostToolUse hook. ~3ms overhead per query. Multi-agent/multi-tool compatible (Claude Code, Codex, Gemini, Cursor). | https://github.com/colbymchenry/codegraph | WATCH — [UNVERIFIED: third-party; architectural pattern relevant] | medium | pending |

---

## Patterns Worth Knowing

### 1. The 5-Level Subagent Tree Changes Orchestration Architecture

The w24 nested subagent feature means compound-brain routines can now delegate recursively: a weekly digest agent can spawn 4 parallel lane agents (level 2), each of which spawns a verifier (level 3), without any of this being written into a single monolithic prompt. The `/agents` view shows the live tree. The 5-level hard cap is the runaway guard — design orchestration to stay at 3 levels (main → lanes → verify) to leave headroom for unexpected delegation.

### 2. Agent Authority Is Now Explicitly Modeled

The w24 hardening establishes a formal trust hierarchy: user messages → full authority; agent-relayed messages → subordinate authority, blocked by auto mode. This is the first explicit trust-tier distinction in Claude Code. Implication for compound-brain: any multi-agent pipeline that previously relied on one agent telling another "the user approved this" can no longer escalate that way. Design pipelines to accumulate approvals at the user tier, not the agent tier. This is a security improvement that changes multi-agent design contracts.

### 3. Sangha Consensus: Multi-Agent Agreement as a Gate

ccswarm's pattern (untrusted, extract the concept): instead of a single agent proceeding when it thinks a plan is good, multiple agents evaluate the same decision independently and must all signal approval before the workflow advances. Applied to compound-brain: before any `NEEDS APPROVAL` action is queued, run a small consensus panel (2-3 agents with different evaluation criteria: safety, correctness, reversibility). Only unanimous approval queues it. This is a structural alternative to single-agent self-assessment.

### 4. Judge-Loop Refinement (Simmer Pattern)

Multi-round iterative output quality: generate → judge against explicit criteria → revise → re-judge → stop when threshold met. The key insight is that the stopping condition is externalized (user-defined criteria in a rubric file) rather than implicit in the LLM's self-assessment. For compound-brain: apply this to research digest generation itself — a judge agent scores the draft digest against the required sections schema before it's written to disk. If the score is below threshold, the draft is revised.

### 5. Git-Native Memory Is Zero-Infra and Commit-Durable

Git notes (`git notes add`) persist as first-class git objects — they survive branches and merges but are not pushed by default (safe by default). For compound-brain: `.brain/` already uses git for persistence; a git-notes-based memory layer for session observations would add durable episodic memory with zero external dependencies, zero schema, and perfect auditability. The write cost (~3ms/event) is negligible for post-session hooks.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| Nested subagent tree (5 levels) | Weekly digest routine | Fork 4 research lanes as level-2 subagents, each spawning a verifier at level-3; wall-clock drops; main session synthesizes only final outputs |
| `--safe-mode` for hook debugging | All hooks + startup troubleshooting | When a hook causes session startup failures, `--safe-mode` isolates it instantly without manual comment-out cycles |
| Agent authority hardening | All multi-agent pipelines | Audit any existing pipeline that relies on agent-to-agent approval escalation — those are now blocked; replace with explicit user-tier approvals |
| `Tool(param:value)` deny rules | `.claude/settings.json` permission gates | Block `Agent(model:opus)` specifically in cron sessions to prevent expensive model selection without blocking all agent spawns |
| Background subagent prompt surfacing | Autonomous routines | Routines blocked on a permission can now surface the prompt to the user instead of silently failing; reduces invisible stalls in weekly digest |
| `sandbox.credentials` | All sessions processing external content | Enable for runs that evaluate third-party patterns to prevent credential leakage via malicious content |
| `fallbackModel` | Cron/scheduled sessions | Set 2-3 fallbacks so weekly digest doesn't stall if primary model is overloaded at scheduled time |
| Sangha consensus pattern | Approval gates for NEEDS APPROVAL items | Run 2-agent consensus panel on queued actions before presenting to user for final sign-off; reduces human review burden |
| Judge-loop refinement (Simmer) | Digest writing step | Run a judge agent against the `validate-digest` schema before writing the final file; no malformed digests reach the queue |
| Git-notes episodic memory | `.brain/` memory layer | Add git-notes-based session observation log to PostToolUse hook (new session facts → git notes → appended to AGENTS.md on next run) |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Append to AGENTS.md — Agent Authority Hardening Rule

**Risk: SAFE** — markdown append to `.brain/AGENTS.md`

Append to AGENTS.md: "From w24 (Claude Code v2.1.172): agent-relayed messages via SendMessage no longer carry user authority; auto mode blocks them. Design multi-agent pipelines to accumulate approvals at the user tier — agent-to-agent approval escalation is now structurally prevented. Audit any pipeline that previously used this pattern."

---

### [SAFE-2] Add Queue Items for Actionable Findings

**Risk: SAFE** — markdown append to `.brain/queue.md`

Add items:
- 013: Audit multi-agent pipelines for reliance on agent-to-agent authority escalation (medium, pending)
- 014: Evaluate `Tool(param:value)` deny rules for cron session permission hardening (medium, pending)
- 015: Trial nested subagent tree (3 levels) in weekly digest research lanes (low, pending)
- 016: Enable `fallbackModel` in settings for scheduled routines (medium, pending — NEEDS APPROVAL for settings change)
- 017: Prototype judge-loop refinement step at end of digest generation (medium, pending)

---

### [SAFE-3] Update Prior Digest Outcome Fields

**Risk: SAFE** — markdown edit to `.brain/knowledge/research/2026-08-04-llm-architecture-digest.md`

From the 2026-08-04 digest, the following ADOPT items can be updated:
- Find #6 (Anti-Fabrication Notifications): already marked `confirmed` in that digest — no change needed
- Find #1 (/doctor): still pending — unchanged
- Find #2 (Stacked skills): still pending — unchanged
No other outcome changes can be confirmed this run without running the features.

---

### [SAFE-4] Draft Candidate Skill — Judge-Loop Refinement

**Risk: SAFE** — create `.brain/candidate-skills/judge-loop-refine/SKILL.md` (under `.brain/`, not under `plugins/` or `.claude/skills/`; drafting does not execute as instructions)

Draft a skill definition for the judge-loop pattern: generate draft → judge against rubric → revise if below threshold → re-judge → stop. Implement using existing subagent primitives + `/goal`. Does NOT get promoted to plugins without human approval.

---

### [NEEDS APPROVAL] Items Deferred

The following items from this digest are NOT auto-applied:

- Enable `sandbox.credentials` — modifies `settings.json` → NEEDS APPROVAL
- Enable `fallbackModel` configuration — modifies `settings.json` → NEEDS APPROVAL
- Add `Tool(param:value)` deny rules — modifies `settings.json` or `.claude/settings.json` → NEEDS APPROVAL
- Hook-level changes for background subagent prompt surfacing — touches `.claude/hooks/` → NEEDS APPROVAL
- Any use of `/ultrareview` or Ultraplan — cloud execution; costs real quota → NEEDS APPROVAL
- Promoting candidate skill drafts to `plugins/` — needs human review of content → NEEDS APPROVAL

---

## Recommended Actions

1. **Audit multi-agent pipelines for the authority-hardening breakage (w24).** Any pipeline that relied on agent-relayed messages carrying user authority is now broken silently — auto mode blocks those messages without error surfacing. Map every `SendMessage` call in `.claude/` hooks and note whether it was trusted. Queue item 013 covers this audit; it is SAFE to plan but NEEDS APPROVAL to change hooks.

2. **Add `fallbackModel` to scheduled session config.** The weekly digest runs at a fixed scheduled time; if the primary model is overloaded, the routine currently stalls and produces nothing. A 2-model fallback chain (primary → secondary) costs nothing and silently recovers. Needs approval to touch settings, but the recommendation is actionable immediately.

3. **Trial the judge-loop refinement pattern on next digest run.** The validate-digest skill (queue 003, already done) provides the schema; adding a judge step before file write would surface structural problems before they land in git. This is implementable with existing subagent primitives in the routine's stored prompt — no new infrastructure needed.

---

## Needs Approval

- **Hook changes after agent authority audit** — touching `.claude/hooks/` requires approval
- **`settings.json` additions** — `sandbox.credentials`, `fallbackModel`, `Tool(param:value)` deny rules all require approval
- **/ultrareview execution** — cloud agent fleet run costs quota; approve before first use
- **Ultraplan execution** — consumes ~33% of 5-hour session quota per run; approve before first use
- **Promoting candidate skill drafts** — content under `.brain/candidate-skills/` to `plugins/` requires human review and approval
- **Ongoing: repo visibility** (queue 007) — this repo remains PUBLIC; no project/service/host names in any `.brain/` content
- **Ongoing: delete public branch** (queue 006) — `claude/cool-heisenberg-2iokix` still needs owner action
