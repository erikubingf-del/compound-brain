# LLM Architecture Digest: 2026-11-16

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** 4-lane research scan covering weeks 30–37 of 2026 and v2.1.319–v2.1.325 release notes.
Last digest: 2026-08-04 (covered w27–w29). No prior digest missed; dedup rule applied.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|------------|---------|
| 1 | Cross-Session Messaging | Sessions discover each other via `ListAgents` and exchange text via `SendMessage`; `@name` in prompt directly messages another live session. macOS/Linux, v2.1.224+. | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 2 | Fork Mode On By Default | Claude can now spawn a fork subagent that inherits the full conversation + prompt cache. Active in interactive sessions without any config. `CLAUDE_CODE_FORK_SUBAGENT=0` to disable. | https://code.claude.com/docs/en/whats-new/2026-w33 | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 3 | Task Tools Retired on Modern Models | `TaskCreate`, `TaskUpdate`, `TodoWrite`, `TaskGet` removed by default on Opus 4.8+, Sonnet 5+, Fable 5+. Re-enable with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`. | https://code.claude.com/docs/en/tools-reference.md#task-tool-availability | ADOPT — action required [VERIFIED: official docs w33] | high | pending |
| 4 | /skill-doctor | Shows context cost and usage frequency per skill in the `/plugin` manager Stats tab. Identifies dead-weight skills that inflate context on every turn. v2.1.252+. | https://code.claude.com/docs/en/whats-new/2026-w36 | ADOPT — [VERIFIED: official docs w36] | high | pending |
| 5 | claude plugin eval | Test a plugin against a Claude-drafted suite of cases; compare with/without plugin baseline; `claude plugin eval init` proposes cases and graders. v2.1.269+. | https://code.claude.com/docs/en/whats-new/2026-w37 | ADOPT — [VERIFIED: official docs w37] | high | pending |
| 6 | Anthropic: Components of Agent Memory | Official research post. Memory hierarchy: transcripts → memory notes → memory representations → injected context. "Dreaming" = offline consolidation pass that corrects errors and promotes facts. Key rule: store only what can't be recovered from the environment (strategies, tested rules — not raw data). | https://www.anthropic.com/research/components-of-agent-memory | ADOPT — [VERIFIED: anthropic.com official blog] | high | pending |
| 7 | 200-Subagent Cap Removed | Per-session subagent hard cap (previously 200) is gone. Concurrency and depth limits (5 levels) still apply. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |
| 8 | Scheduled Tasks Ask Before Skills | From v2.1.325: scheduled tasks and `/loop` ask before running any skill that declares `allowed-tools` or hooks. Affects unattended routines that invoke skills. | https://releases.sh/anthropic/claude-code-releases.md | WATCH — [VERIFIED: v2.1.325 release notes] | high | pending |
| 9 | permissions.denyInsteadOfPrompting | New setting: blocked tool calls are denied (turn continues) rather than waiting on a prompt. Useful for autonomous routines where a hanging prompt kills the run. | https://releases.sh/anthropic/claude-code-releases.md | WATCH — [VERIFIED: v2.1.319 release notes] | high | pending |
| 10 | Code Mode (Experimental) | v2.1.323 opt-in: Claude writes JavaScript to call its tools rather than using the native tool protocol. No implementation without review — experimental/unstable. | https://releases.sh/anthropic/claude-code-releases.md | WATCH — [VERIFIED: v2.1.323 release notes; experimental] | medium | pending |
| 11 | Auto Mode Default (Aug 14) | Auto mode is now the default permission mode on Pro/Max/Team. Classifier calls no longer count toward usage limits. Existing sessions unaffected unless user accepts the one-time switch prompt. | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | confirmed |
| 12 | /design Command — Artboard Workflow | Research preview: Claude Design's artboard workflow in CLI and Desktop. Drafts editable UI artboards via artifacts; you pick one and Claude implements it. | https://code.claude.com/docs/en/whats-new/2026-w34 | WATCH — [VERIFIED: official docs w34; research preview] | medium | pending |
| 13 | Claude Fable 5.2 | New default Fable model: 1M context, $8/$40 per MTok, $0.20/M cache reads. `claude-fable-5-2` model ID. v2.1.321+. | https://releases.sh/anthropic/claude-code-releases.md | WATCH — [VERIFIED: v2.1.321 release notes] | high | pending |
| 14 | NVIDIA SkillEvaluator | Tiered skill evaluation: Tier 1 offline deterministic gates (schema, security, PII, code integrity), CI gating at min-score 70. Caveat: ACES paper (Aug 2026) shows static gates have near-zero correlation with runtime success. | https://github.com/NVIDIA/SkillEvaluator | TEST — [UNVERIFIED: third-party; pattern extractable, no install] | medium | pending |
| 15 | --restricted Flag | Starts a Claude Code session without command-running tools or user/project settings. Designed for eval harnesses on shared machines. | https://code.claude.com/docs/en/whats-new/2026-w35 | WATCH — [VERIFIED: official docs w35] | high | pending |

---

## Patterns Worth Knowing

### 1. Cross-Session Messaging as a Multi-Agent Control Bus

Sessions now discover and message each other natively. For compound-brain this is the right primitive for a supervisor pattern: a main session can spawn a research fork, then @ the fork later to retrieve its findings without re-explaining context. The `ListAgents` + `SendMessage` tools are the low-level API; the `@name` syntax in the prompt is the high-level shorthand. Messages are text only — not conversation history or file contents — so the protocol is appropriately bounded.

### 2. Fork Mode Default Changes the Delegation Model

Fork mode on by default means Claude can now delegate a side task (e.g. drafting tests, running a research lane) to a subagent that already has the full conversation in its cache. Previously, every fork started from scratch and needed re-briefing. This directly improves the weekly digest routine: a fork launched for one research lane doesn't need the AGENTS.md preamble re-explained.

### 3. Task Tools Retirement — Queue Pattern Needs Audit

`TaskCreate`, `TaskUpdate`, `TodoWrite` are gone on Sonnet 5, Fable 5, and later models. If compound-brain's `.brain/queue.md` relies on these tools being invoked as Claude tools, those calls silently do nothing without the env var override. The markdown-queue pattern in `.brain/queue.md` is not affected — that's just file writes — but any skill or hook that calls the Task tools directly needs the `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` flag or a migration to file-based tracking.

### 4. Anthropic Memory Hierarchy: Small Injected Layer, Offline Dreaming

Anthropic's Nov 2026 research formalizes a four-layer memory model:
1. Transcripts (full event log — not injected)
2. Memory notes (observations written during a session)
3. Memory representations (structured forms: wikis, linked pages)
4. Injected context (small, loaded at session start)

The key operational insight: injected context must stay small (every injected note consumes tokens; long instruction files reduce adherence). "Dreaming" — an offline pass that reviews transcripts and notes — is what prevents note rot: it corrects errors, merges duplicates, and promotes facts up the hierarchy. This is the architecture for `.brain/`; the current memory layout maps closely but lacks the explicit dreaming pass.

### 5. Scheduled Tasks Ask Before Skills (v2.1.325) — Unattended Loop Hardening

From v2.1.325: scheduled tasks and `/loop` ask before running any skill that declares `allowed-tools` or hooks. This is a safety hardening — it prevents an unattended run from silently invoking a privileged skill. For the compound-brain weekly routine, it means any skill this session uses that declares `allowed-tools` will trigger a prompt. Since this session is unattended, that prompt blocks indefinitely. The fix: either approve the specific skill's `allowed-tools` declaration in settings, or confirm this session's skills don't declare `allowed-tools`.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| Cross-session messaging | Weekly routine + multi-session orchestration | Supervisor session delegates research lanes to forks via `@name`; results arrive without re-briefing |
| Dreaming pass | `.brain/memory/` consolidation | Offline pass over transcripts + notes corrects stale facts, prevents knowledge rot across runs |
| Small injected layer rule | `.brain/memory/project_context.md` and injected context | Audit injected files for size; promote verbose content to deeper layers (representations), keep injected index tiny |
| /skill-doctor | compound-brain plugin skills | Run `/skill-doctor` to identify skills that inflate context without activation; remove dead weight |
| claude plugin eval | compound-brain skill validation | Draft eval suite for `brain-digest` and `brain-orient` skills to verify they produce correct outputs |
| permissions.denyInsteadOfPrompting | Routine settings | Add this setting to prevent unattended runs from hanging on blocked tool calls |
| Task tools retirement audit | `.brain/queue.md` and any skills using TaskCreate | Verify no brain skill or hook calls Task tools; if so, add `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` or rewrite as file writes |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Update Prior Digest Outcome Fields

**Risk: SAFE** — markdown edits under `.brain/**`

Update 2026-08-04 digest outcome fields:
- #4 `/fork` vs `/subtask` distinction: outcome → confirmed (w32/w33 provide full detail; fork mode is now default; /subtask creates in-session forks)
- #5 Subagents background by default: outcome → confirmed (default in all sessions per w33)
- #6 Anti-fabrication background task notifications: already confirmed
- #7 Session-wide caps: outcome → superseded (200-subagent cap removed in w32; WebSearch cap still applies)
- #9 Background agents auto-PR: outcome → confirmed-modified (w32 clarifies: auto-PR only when the task calls for it, not automatic; CLAUDE.md git instructions are respected)
- #11 Sonnet 5 1M context: outcome → confirmed (Opus 5, Fable 5.1, Fable 5.2 all 1M context now standard)
- #12 MCP tool calls >2min auto-background: outcome → confirmed (v2.1.319 MCP tasks in terminal formalized this)
- #13 In-app browser on Desktop: outcome → confirmed (w36 adds background CU; full browser in w28)

### [SAFE-2] Add Queue Items for Priority Work

**Risk: SAFE** — markdown append to `.brain/queue.md`

New items to add:
- 013: Audit brain skills for Task tool usage → check if any skill calls TaskCreate/TaskUpdate; migrate or flag before Sonnet 5/Fable 5 becomes universal default (high, pending)
- 014: Run /skill-doctor on compound-brain plugin → identify dead-weight skills inflating context (medium, pending)
- 015: Draft eval suite for brain-digest skill using `claude plugin eval` (medium, pending)
- 016: Add `permissions.denyInsteadOfPrompting` to routine settings — prevents unattended runs from hanging (medium, NEEDS APPROVAL — settings change)
- 017: Audit injected context layer size — ensure .brain memory files loaded at session start are under ~2k tokens each (low, pending)
- 018: Design a dreaming pass for .brain memory consolidation based on Anthropic memory research (low, pending)

### [SAFE-3] Append Learnings to AGENTS.md

**Risk: SAFE** — append to `.brain/AGENTS.md`

---

## Recommended Actions

1. **Audit Task tool usage in all brain skills immediately.** `TaskCreate`, `TaskUpdate`, `TodoWrite` are removed on Sonnet 5+. If any brain skill or hook calls these, it silently does nothing on modern models unless `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` is set. This is a potential silent regression with no error. Run a grep across `.claude/`, `plugins/`, and `.brain/` for `TaskCreate|TaskUpdate|TodoWrite`. (SAFE — read-only audit.)

2. **Run `/skill-doctor` in the next attended session.** It shows context cost and usage frequency per skill. Compound-brain has a growing plugin skill set. Zero-activation skills inflate every session's context budget. Candidates for removal or consolidation would become visible immediately. (SAFE — read-only audit. Skill removal NEEDS APPROVAL.)

3. **Design a dreaming pass for `.brain/memory/`.** The Anthropic memory research formalizes exactly the architecture `.brain/` is approximating. The missing piece is an offline consolidation step: a scheduled routine that reviews recent transcripts and existing memory notes, corrects stale entries, and promotes structured facts to `knowledge/`. The design can be written as a `.brain/knowledge/resources/` spec (SAFE); implementing it as a cron or hook NEEDS APPROVAL.

---

## Needs Approval

- **Task tool migration** — if any skill/hook calls TaskCreate/TaskUpdate, changing those calls touches plugin code
- **`CLAUDE_CODE_ENABLE_TODO_TOOLS=1`** — adding an env var to any settings file or hook requires approval
- **`permissions.denyInsteadOfPrompting` setting** — settings file change
- **Skill removal from compound-brain plugin** — after /skill-doctor audit
- **Dreaming pass cron/hook** — once designed; running it on a schedule is a cron change
- **Repo visibility** (carried from prior digest) — this brain repo is PUBLIC; recommend private
- **Queue 002: CLAUDE.md audit** (carried) — proposal-002 written; applying it touches CLAUDE.md
- **Queue 006: Delete public branch** `claude/cool-heisenberg-2iokix` — owner action
