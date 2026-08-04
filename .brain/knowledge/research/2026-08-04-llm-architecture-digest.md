# LLM Architecture Digest: 2026-08-04

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** this date covers two runs that were merged into one record —
the bootstrap run (routine, queue, validate-digest, SAGE spec, proposal-002)
and a full 4-lane research scan. An earlier draft of this digest stated "no
new candidates this run"; that was written before the research scan and is
superseded by the 15 findings below. Kept as one file per date so the Step 0
dedup rule reads a single, non-contradictory record.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | /doctor — Full Setup Checkup | Diagnoses AND fixes: checks unused skills/MCP/plugins vs context cost, deduplicates CLAUDE.md against checked-in copies, proposes trimming content Claude could derive from codebase, flags slow hooks. Alias: /checkup. | https://code.claude.com/docs/en/commands#all-commands | ADOPT — [VERIFIED: official docs w28] | high | pending |
| 2 | Stacked Skill Invocations | `/skill-a /skill-b do XYZ` loads all leading skills (up to 5), not only the first. Enables composite skill chains without manually loading each. | https://code.claude.com/docs/en/whats-new/2026-w27 | ADOPT — [VERIFIED: official docs w27] | high | pending |
| 3 | "Always Allow" Permissions Persist Across Worktrees | Permission rules now save at repo root so approvals granted in a git worktree persist across sessions and all worktrees in that repo. Eliminates repeated permission prompts for autonomous routines. | https://code.claude.com/docs/en/whats-new/2026-w29 | ADOPT — [VERIFIED: official docs w29] | high | pending |
| 4 | /fork vs /subtask Distinction | `/fork` now copies conversation into a new BACKGROUND SESSION with its own row in `claude agents`. `/subtask` is the new name for what `/fork` used to do (in-session forked subagent). Architectural change for orchestration patterns. | https://code.claude.com/docs/en/whats-new/2026-w29 | ADOPT — [VERIFIED: official docs w29] | high | pending |
| 5 | Subagents Background by Default | Claude keeps working while subagents run; picks up results when they finish. Subagent still runs foreground when result is needed before continuing. Pin behavior with `background` frontmatter field in agent definition. | https://code.claude.com/docs/en/sub-agents#run-subagents-in-foreground-or-background | ADOPT — [VERIFIED: official docs w27] | high | pending |
| 6 | Anti-Fabrication: Background Task Notifications | Background task notifications now EXPLICITLY STATE that no human input has occurred since the last genuine user message, preventing fabricated in-transcript approvals from being acted on. Critical for scheduled/cron routines. | https://code.claude.com/docs/en/whats-new/2026-w28 | ADOPT — [VERIFIED: official docs w28] | high | confirmed |
| 7 | Session-Wide Caps for WebSearch and Subagents | WebSearch and subagent spawns each default to 200 per session. Tunable via `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` and `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`. Runaway loop protection for autonomous routines. | https://code.claude.com/docs/en/whats-new/2026-w29 | WATCH — [VERIFIED: official docs w29] | high | pending |
| 8 | Hook Matchers: Hyphenated Identifiers Now Exact-Match | Hook matchers with hyphenated identifiers like `code-reviewer` now exact-match instead of substring-matching. Use `mcp__brave-search__.*` to match ALL tools from a hyphenated MCP server. Potential breaking change for existing hooks. | https://code.claude.com/docs/en/whats-new/2026-w27 | WATCH — [VERIFIED: official docs w27] | high | pending |
| 9 | Background Agents Auto-PR on Worktree Completion | Background agents launched from `claude agents` now commit, push, and open a draft PR when they finish code work in a worktree, instead of stopping to ask. Changes autonomous coding workflow defaults. | https://code.claude.com/docs/en/whats-new/2026-w27 | WATCH — [VERIFIED: official docs w27] | high | pending |
| 10 | Artifacts: Live Data via MCP Connectors | Published artifacts can call MCP connectors on each view — dashboards show live data, not snapshots. Each call runs through the viewer's own connections; viewers approve access before first connector call. Also: public sharing links, editor roles for Team/Enterprise. | https://code.claude.com/docs/en/artifacts#pull-live-data-with-mcp-connectors | WATCH — [VERIFIED: official docs w29] | high | pending |
| 11 | Claude Sonnet 5: 1M-Token Context + Adaptive Thinking Default | New default model for Pro/Team Standard/Enterprise. Native 1M-token context window changes context budget calculations (prior 5% rule applied to 200k; now applies to 1M). Adaptive thinking on by default. API: $2/$10/MTok through Aug 31. | https://code.claude.com/docs/en/whats-new/2026-w27 | WATCH — [VERIFIED: official docs w27] | high | pending |
| 12 | MCP Tool Calls >2min Auto-Background | Long-running MCP tool calls now move to background automatically after 2 min so session stays usable. Tune or disable with `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS`. | https://code.claude.com/docs/en/whats-new/2026-w29 | WATCH — [VERIFIED: official docs w29] | medium | pending |
| 13 | In-App Browser on Desktop | Claude Code Desktop now has built-in sandboxed browser: Claude can browse external docs/designs, click/read/interact, with safety classifiers reviewing external actions. Separate from Claude in Chrome (CLI-driven). | https://code.claude.com/docs/en/desktop#browse-external-sites | WATCH — [VERIFIED: official docs w28] | high | pending |
| 14 | Agno — Multi-Agent Framework, Runtime + Control Plane | Third-party open-source: orchestrates agents as multi-agent teams or step-based workflows; stateless FastAPI runtime; horizontally scalable; memory/knowledge/state/guardrails/HITL/context compression/MCP/A2A built in. Run in your cloud. | https://www.agno.com/agentos | WATCH — [UNVERIFIED: third-party; patterns extractable but no install] | medium | pending |
| 15 | Explore Agent Inherits Session Model | Built-in Explore agent now inherits main session's model (capped at Opus) instead of always running on Haiku. Better research quality in the same session. | https://code.claude.com/docs/en/whats-new/2026-w27 | ADOPT — [VERIFIED: official docs w27] | high | pending |

---

## Patterns Worth Knowing

### 1. /doctor as Living CLAUDE.md Auditor

`/doctor` (now at v2.1.205+) solves the CLAUDE.md audit problem (queue 002) natively and semi-automatically. It doesn't just report — it proposes trims and deduplication with confirmation before changing anything. Run it before any manual CLAUDE.md audit to get a baseline of what's actually stale or derivable from the codebase. The "flags slow hooks" capability is also relevant for compound-brain: hooks that block session startup have disproportionate cost.

### 2. The /fork + /subtask Orchestration Architecture

These two commands now represent two distinct orchestration tiers:
- `/subtask` — lightweight in-session fork; shares the parent context window; synchronous; good for isolated sub-problems within a session
- `/fork` — full new background session in `claude agents`; own context window, own model, own tool permissions; asynchronous; appears as a row in agent view

For compound-brain routines, `/fork` is the right primitive for spinning off independent research lanes without blocking the main session. Background subagents (now default) handle the synchronization.

### 3. Session-Wide Caps as Autonomous Safety Rail

WebSearch (200/session) and subagent spawns (200/session) are now hard defaults that prevent runaway loops in autonomous sessions. These are the right guardrails for the Ralph Loop pattern — the loop terminates naturally if it hits the cap, rather than running indefinitely. Combine with the anti-fabrication notification language (which this session benefits from) for safe cron execution.

### 4. Stacked Skills as Composite Skill Chains

`/skill-a /skill-b do XYZ` loading up to 5 skills enables composition without new skill files. For compound-brain: a research session could run `/dataviz /review analyze this agent architecture` to load both skills simultaneously. This replaces the pattern of writing wrapper skill files that just import other skills.

### 5. "Always Allow" Persistence Across Worktrees Changes Permission Strategy

Previously, permission approvals were session-scoped. Now they save at repo root and persist across sessions and worktrees. This means: approve a tool once in a compound-brain session, and all future sessions (including cron/scheduled sessions) in that repo get the same permission without prompting. The right strategy is: run one explicit setup session with permission approvals, commit `.claude/settings.local.json`, and all autonomous sessions inherit it.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| /doctor audit | CLAUDE.md + skills/MCP optimization | Run /doctor before queue item 002 manual audit — it catches derivable content and deduplicates automatically; human reviews the proposed changes |
| Stacked skill invocations | Research routines | Chain `/dataviz /review` or `/dataviz /simplify` without wrapper files; reduces skill file proliferation |
| /fork for research lanes | Weekly digest routine | Fork 4 independent research lanes instead of sequential WebSearch; results arrive async; main session synthesizes |
| "Always allow" persistence | All autonomous routines | One setup session eliminates repeated permission prompts in all cron/scheduled sessions; commit approved permissions |
| Session-wide caps | All autonomous routines | Explicit tuning of MAX_WEB_SEARCHES and MAX_SUBAGENTS sets safe ceilings for this digest routine (current searches: ~8; well under 200) |
| Sonnet 5 1M context | CLAUDE.md budget calculations | Prior 5% rule assumed 200k context (10k tokens). At 1M, 5% = 50k tokens. Revisit whether the ≤200-line rule is still the right proxy or whether token count is more precise. |
| Background agents auto-PR | Compound-brain development | When brain improvement work runs in a worktree, background agent now auto-opens draft PR — no manual push step needed |
| Agno control plane patterns | Department/runtime model | Extract HITL and context compression patterns for native reimplementation in .brain; do NOT install Agno code |

---

## AUTO-APPLY QUEUE

### [APPLIED] Bootstrap items — all SAFE (markdown under `.brain/**` only)

Applied this run:
- `.brain/routines/weekly-digest-prompt.md` — routine source of truth; the repo copy wins over the stored prompt.
- `.brain/AGENTS.md` (Ralph-loop learnings log) and `.brain/queue.md` (task queue).
- Queue 003: `knowledge/skills/validate-digest.md` typed-contract validator.
- Queue 005: `knowledge/resources/sage-novelty-gate-spec.md` design spec (prototype code deferred — NEEDS APPROVAL).
- Queue 002: `knowledge/decisions/proposal-002-claude-md-hierarchy.md` — writing the proposal is SAFE; applying it is NEEDS APPROVAL.
- Both digests relocated from the gitignored `knowledge/daily/` to tracked `knowledge/research/`, and the routine repointed there, so digests survive container teardown and the dedup rule has something to read.

### [SAFE-1] Update Prior Digest Outcome Fields

**Risk: SAFE** — markdown edit under .brain/**

Items from 2026-08-03 that are now confirmed implemented:
- ADOPT-1 (Ralph Loop): CONFIRMED — `.brain/AGENTS.md` created, routine reads it
- ADOPT-3 (Queue-Based Markdown OS): CONFIRMED — `.brain/queue.md` created
- ADOPT-5 (Outcome-Tracked Digest Entries): CONFIRMED — this and prior digest include confidence/outcome columns

Update 2026-08-03 digest outcome fields accordingly. ✅ (Applied below in this session)

---

### [SAFE-2] Add Queue Item for /doctor Test Run

**Risk: SAFE** — markdown append to .brain/queue.md

Add item 006: run `/doctor` and review its CLAUDE.md audit output before attempting manual queue-002 audit.

---

### [SAFE-3] Note Hook Matcher Breaking Change

**Risk: SAFE** — append to .brain/AGENTS.md

Brain hooks using hyphenated MCP server names need audit: if any hook matcher previously relied on substring-matching `brave-search` to catch all brave-search tools, it now exact-matches the literal string `brave-search` (a tool named exactly that). Use `mcp__brave-search__.*` for catch-all pattern. This is a potential silent hook breakage.

---

## Recommended Actions

1. **Run `/doctor` before attempting queue-002 (CLAUDE.md audit).** The `/doctor` command at v2.1.205+ proposes CLAUDE.md trims, deduplicates local vs checked-in content, and identifies rules Claude could derive from the codebase. It does this with confirmation before changes — exactly what the manual audit planned to do. Run it first, review its output, then do manual follow-up. Eliminates duplicate work.

2. **Audit hooks for hyphenated-name breakage.** The hook matcher change in w27 is a potential silent failure: hooks that relied on substring-matching hyphenated identifiers now exact-match. Check `.claude/hooks/` for any matcher that contains a hyphen. If it's meant to be a catch-all for an MCP server, update to `mcp__server-name__.*` pattern. This needs approval to touch hooks.

3. **Plan a "permission setup session" to persist approved tools.** Now that "always allow" saves at repo root and persists across worktrees/sessions, one deliberate approval session eliminates prompts for all future cron runs. Identify the tools this digest routine needs (WebSearch, Read, Write, Bash for git), approve them, and commit `.claude/settings.local.json`. Needs approval before touching settings.

---

## Needs Approval

- **Hook matcher audit and fixes** — touching `.claude/hooks/` requires approval
- **Permission setup session** — modifying `.claude/settings.local.json` or similar requires approval
- **CLAUDE.md changes from /doctor output** — touching CLAUDE.md content requires approval
- **Testing /doctor in this repo** — running /doctor is a read-only audit but its proposed fixes touch CLAUDE.md; approve the fix step separately
- **Apply proposal-002** (CLAUDE.md split, 357 → ~140 root lines) — edits root `CLAUDE.md` and `core/BRAIN.md`
- **Any SAGE prototype code** — `knowledge/resources/sage-novelty-gate-spec.md` defines it; code is not markdown-SAFE
- **Repo visibility** — this repo is PUBLIC (`visibility: public`, confirmed via GitHub API 2026-08-04). A brain that governs autoresearch, approvals, and autonomy depth is a poor fit for a public repo. Recommend switching to private; until then, no project, service, host, or strategy names may appear anywhere under `.brain/`.
