# LLM Architecture Digest: 2026-08-03

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | Ralph Loop | Filesystem-as-memory autonomous loop: fresh context each run, state on disk, learnings compound into AGENTS.md | https://github.com/snarktank/ralph | ADOPT | high | confirmed — .brain/AGENTS.md created 2026-08-04; routine reads it each run |
| 2 | Karpathy LLM Wiki | Compile raw sources into a structured Markdown wiki once; subsequent queries hit the wiki, not raw docs | https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f | ADOPT | high | pending |
| 3 | Spec-Driven Development / UltraPlan | Versioned spec as source of truth; Claude Code skill that explores codebase in parallel then emits plan before touching code | https://github.com/6missedcalls/ultraplan | ADOPT | high | pending |
| 4 | Queue-Based Markdown OS | Zero-infra task queue in a markdown file; agents claim, execute, and mark done without any external broker | https://github.com/ithiria894/awesome-claude-code-workflows | ADOPT | high | confirmed — .brain/queue.md created 2026-08-04 with ID/Task/Status/Priority/Claimed By schema |
| 5 | Outcome-Based Skill Memory | Memory entries carry confidence + last_outcome; PostToolUse hook writes outcome back; store self-improves | https://github.com/hesreallyhim/awesome-claude-code | ADOPT | high | confirmed — confidence + outcome columns added to all digest top_finds tables starting 2026-08-03 |
| 6 | SAGE Novelty Gate | Write-side memory controller using density estimation to classify incoming facts as ADD/NOOP/MERGE; 3.4x API cost reduction | https://arxiv.org/abs/2605.30711 | TEST | medium | pending |
| 7 | Anti-Hallucination Schema Enforcement | Typed output contracts between skills; receiving skill rejects malformed handoffs | https://github.com/hesreallyhim/awesome-claude-code | ADOPT | high | pending |
| 8 | Claude Code Agent Checkpointing | Native: session-level checkpoint+rewind via /rewind; subagent edits explicitly NOT restored per docs | https://code.claude.com/docs/en/checkpointing.md | WATCH — [UNVERIFIED: "full agent-tree state" claim exceeds official docs] | low | pending |
| 9 | Anthropic Dreaming Pass | Third-party blog claim only — not found in official Anthropic docs | — | SKIP — [UNVERIFIED: source was non-official] | low | invalidated |
| 10 | Progressive Disclosure CLAUDE.md | Hierarchical CLAUDE.md (root + per-dir), under 200 lines, each rule falsifiable, ≤5% context budget | https://dev.to/nishilbhave/claudemd-best-practices-the-complete-2026-guide-435j | ADOPT | high | pending |
| 11 | Hooks + Git Worktrees for context isolation | Per-worktree CLAUDE.md + hook logic that auto-scopes skills; parallel agents cannot share filesystem state | https://github.com/hesreallyhim/awesome-claude-code | ADOPT | high | pending |
| 12 | MCP 2026-07-28 Stateless Spec | MCP moved to request/response model; serverless/edge deployable; cacheable list results; vendor-neutral (Linux Foundation) | https://blog.modelcontextprotocol.io/posts/2026-07-28/ | WATCH — [VERIFIED: official MCP blog + claude.com/blog] | high | pending |
| 13 | DeerFlow 2.0 SuperAgent Harness | Long-horizon orchestration: parallel sandboxed subtasks, Markdown-defined skill modules, model-agnostic | https://github.com/bytedance/deer-flow | WATCH | medium | pending |
| 14 | Hybrid Graph Memory (Mem0/Zep/A-MEM) | Three-tier memory: vector (episodic) + temporal knowledge graph (relational) + KV (procedural) | https://vectorize.io/articles/best-ai-agent-memory-systems | TEST | medium | pending |
| 15 | Dynamic Workflows (Workflows feature) | Dozens–1000 parallel agents per run; available on all paid plans (not Enterprise-only); confirmed standard feature v2.1.154+ | https://code.claude.com/docs/en/workflows.md | WATCH — [VERIFIED: capability real; tier/preview claims in prior draft were incorrect] | high | pending |

---

## Patterns Worth Knowing

### 1. Ralph Loop: Filesystem as Durable Memory, Context Wipe as Feature

Each agent run is a fresh context window. State (spec, progress, learnings) lives on disk in `AGENTS.md`, `progress.txt`, `prd.json`. After each run, the agent appends to `AGENTS.md`; since coding tools re-read that file at startup, **instructions compound across runs without accumulating token overhead**. Failures become diagnostic data; an external verifier (tests, linter, critic agent) drives the retry signal — not the LLM's self-assessment. Directly solves "context rot" (attention degradation as context fills).

### 2. Spec-First Execution: Plan Lives in a File, Not a Prompt

The four-phase pattern (Specify → Plan → Tasks → Implement) externalizes intent into a versioned artifact that outlives the session. Planning runs in a separate context window so it doesn't pollute working memory. The spec is the loop's termination condition and progress oracle — the agent can always diff "what's done" against "what was promised" without re-deriving intent from conversation history.

### 3. Typed Skill Contracts: Skills as a Pipeline, Not a String Chain

Skills emit typed YAML/Markdown deliverables. Downstream skills validate the schema and refuse malformed handoffs. This turns a skill pipeline from a string-passing chain into a typed contract system where failures surface at the boundary, not silently downstream. Combines naturally with outcome-based confidence scoring on each memory entry.

### 4. Write-Side Memory Control (SAGE Pattern)

Nearly all memory work focuses on retrieval (read side). SAGE addresses the write side: a density estimator over memory embeddings classifies incoming facts as ADD (novel), NOOP (redundant), or MERGE (uncertain). Only uncertain cases hit an expensive LLM merge step. Result: 3.4x API cost reduction in write phase. Critical for long-running agents whose memory stores otherwise bloat.

### 5. Progressive Disclosure CLAUDE.md: Every Rule is Falsifiable

Root CLAUDE.md is ≤200 lines, consuming ≤5% of context at session start. Each rule passes the test: "Would Claude err in a real session without this?" Rules that don't pass are deleted. Style/domain rules go into subdirectory CLAUDE.md files, not root. This is the Anthropic-stated target — not just community preference.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| Ralph Loop structure | Scheduled routines (`/loop` skill, daily digest runner) | Routine survives context rot; each run is clean; learnings compound into AGENTS.md across weeks |
| Karpathy LLM Wiki | `.brain/knowledge/` library | Convert raw research dumps into a compiled, interlinked wiki with lint/staleness pass; query cost drops dramatically |
| Queue-Based Markdown OS | Multi-project task coordination | Replace ad-hoc task notes with a markdown queue agents can self-coordinate against; no infra needed |
| Typed Skill Contracts | Skill-to-skill handoffs in the brain | Add typed output schemas to research → digest → brain-update pipeline; catch hallucinated handoffs at boundary |
| Outcome-Based Skill Memory | Research digest quality tracking | Each digest entry carries a `confidence` + `outcome`; `outcome` written back after each weekly cycle by `PostToolUse` hook |
| Progressive Disclosure CLAUDE.md | Root CLAUDE.md + project CLAUDE.md files | Audit and trim to ≤200 lines; push project-specific rules into per-project `.brain/projects/<project>/CLAUDE.md` files |
| Agent Checkpointing (native) | All scheduled routines | Enable checkpoint on long-running routines so they survive container restarts and session limits |
| Hooks + Worktrees isolation | Parallel subagent research lanes | Each research lane gets its own worktree; skills auto-scope; no cross-contamination of intermediate findings |

---

## AUTO-APPLY QUEUE

### [ADOPT-1] Ralph Loop Structure for Scheduled Routines

**Risk: SAFE**

This digest runner already approximates the Ralph Loop. Make it explicit:

1. Add `AGENTS.md` to `.brain/` root:
   ```
   # Brain Agent Learnings
   [append-only log of cross-run insights from scheduled routines]
   ```
2. At the top of each scheduled routine prompt, add: "Read `.brain/AGENTS.md` for prior learnings before starting."
3. At the end of each routine, append a 1-3 line "What I learned this run" to `.brain/AGENTS.md`.
4. Keep each routine's context window clean: no carry-over from prior runs except what's in files.

**Files to create/edit:** `.brain/AGENTS.md` (new), add read instruction to each routine's stored prompt.

---

### [ADOPT-2] Typed Output Schema for Digest → Brain Pipeline

**Risk: SAFE**

1. Add a `schema:` block to this digest template (after the header):
   ```yaml
   schema_version: "1.0"
   required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions]
   top_finds_required_fields: [name, description, url, classification]
   ```
2. Create a `.brain/skills/validate-digest.md` skill that reads a digest file and fails if any required section or field is missing.
3. Wire `validate-digest` as a PostToolUse hook on the digest-write step.

**Files to create:** `.brain/skills/validate-digest.md`, add schema block to this digest template.

---

### [ADOPT-3] Queue-Based Markdown OS for Brain Task Coordination

**Risk: SAFE**

1. Create `.brain/queue.md`:
   ```markdown
   # Brain Task Queue
   | ID | Task | Status | Blocked By | Claimed By |
   |----|------|--------|------------|------------|
   | 001 | Weekly LLM digest | pending | — | — |
   | 002 | Project market scan | pending | — | — |
   ```
2. Each scheduled routine claims its row at start and marks done at end.
3. Add a `check-queue` step at the start of each routine: if a higher-priority task is unclaimed, handle it first.

**Files to create:** `.brain/queue.md`

---

### [ADOPT-4] Progressive Disclosure CLAUDE.md Audit

**Risk: SAFE**

1. Read the current root `CLAUDE.md` (if it exists).
2. For each rule, apply the falsifiability test: "Would Claude err in a real session without this line?"
3. Move project-specific rules to `.brain/projects/<project>/CLAUDE.md`.
4. Move brain-maintenance rules to `.brain/CLAUDE.md`.
5. Keep root CLAUDE.md under 200 lines. Target: ≤5% of a 200k context window = ≤10k tokens of CLAUDE.md content.

**Files to edit:** Root `CLAUDE.md` (if it exists), create `.brain/CLAUDE.md`, `.brain/projects/<project>/CLAUDE.md`.

---

### [ADOPT-5] Outcome-Tracked Digest Entries

**Risk: SAFE**

Each `top_finds` entry in future digests should include:
```yaml
confidence: medium  # low/medium/high
outcome: pending    # pending/confirmed/invalidated
outcome_date: ~
```

After each weekly cycle, the next digest runner checks prior digests for `ADOPT` items and updates `outcome` field based on whether the pattern was implemented and produced value.

**Files to edit:** This digest template (add confidence/outcome fields to top_finds table). Retroactively add to this digest's entries.

---

### [ADOPT-6] Agent Checkpointing — REMOVED ⚠️

**[UNVERIFIED — not implemented]**

The prior claim ("save and resume full agent-tree state across sessions, beta") was sourced from a non-official third-party blog. Official docs (https://code.claude.com/docs/en/checkpointing.md) show checkpointing is session-level only, and explicitly state subagent edits are NOT restored on rewind. Config change would have been based on a fabricated feature description. No implementation.

---

## Recommended Actions

1. **Create `.brain/AGENTS.md` immediately.** This single file makes every future routine smarter by compounding cross-run learnings. Zero infrastructure cost. Start populating it from this digest run (first entry: "Ralph Loop is the right structure for all scheduled routines — implement it.").

2. **Implement the Queue-Based Markdown OS (ADOPT-3) before next week's digest.** The live trading project runs real money. A shared task queue lets the brain prioritize safely — if a market anomaly is detected and queued, the next scheduled routine will see it and act rather than proceeding with its planned work blindly.

3. **Audit and split CLAUDE.md into hierarchical files (ADOPT-4).** This is the highest-leverage single action for reducing context waste across every brain session. Do it as part of the next `/init` or brain maintenance pass.

## Needs Approval

- ADOPT-4 (CLAUDE.md audit): touching CLAUDE.md content requires explicit approval per SAFE rules.
- ADOPT-2 (validate-digest hook wiring): PostToolUse hook changes require approval.
