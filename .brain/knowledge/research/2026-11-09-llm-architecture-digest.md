# LLM Architecture Digest: 2026-11-09

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** covers official Claude Code releases w30–w37 (Jul 20 – Sep 11, 2026) plus
community/research finds. Prior digests covered through w29. Gap since last run: ~3 months
(2026-08-04 → 2026-11-09). No weeks 38+ found on official docs at time of run.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|------------|---------|
| 1 | /skill-doctor | Shows context cost and usage frequency per skill; helps identify unused/expensive skills in a plugin or project | https://code.claude.com/docs/en/whats-new/2026-w36 | ADOPT — [VERIFIED: official docs w36] | high | pending |
| 2 | `claude plugin eval` | Runs a plugin against a test-case suite, scores results, compares against no-plugin baseline; `init` drafts cases for you | https://code.claude.com/docs/en/whats-new/2026-w37 | ADOPT — [VERIFIED: official docs w37] | high | pending |
| 3 | Cross-Session Messaging | macOS/Linux: sessions can message each other with `SendMessage`, find each other with `ListAgents`; also available on Bedrock/GCP/Foundry and Windows (w34) | https://code.claude.com/docs/en/whats-new/2026-w32 | ADOPT — [VERIFIED: official docs w32] | high | pending |
| 4 | Fork Mode On By Default | Interactive sessions now have fork mode on; Claude delegates side tasks to background subagents without being asked | https://code.claude.com/docs/en/whats-new/2026-w33 | ADOPT — [VERIFIED: official docs w33] | high | pending |
| 5 | Concise Output Style | Built-in output style: leads with result, skips preamble/narration; set `outputStyle: Concise` in settings or via `/config` | https://code.claude.com/docs/en/whats-new/2026-w34 | ADOPT — [VERIFIED: official docs w34] | high | pending |
| 6 | `--restricted` Mode | Starts Claude Code without command-running tools, WebFetch, or project settings; hardens eval harnesses on shared machines | https://code.claude.com/docs/en/whats-new/2026-w35 | ADOPT — [VERIFIED: official docs w35] | high | pending |
| 7 | Subagent Partial Return + Resume | Subagent that hits `maxTurns` returns partial output (marked partial) instead of appearing done; parent can resume it via `SendMessage` | https://code.claude.com/docs/en/whats-new/2026-w35 | ADOPT — [VERIFIED: official docs w35] | high | pending |
| 8 | Auto Mode Now Default (Aug 14) | Auto mode became the default permission mode for new sessions on Pro, Max, and Team as of Aug 14, 2026 | https://code.claude.com/docs/en/whats-new/2026-w32 | WATCH — [VERIFIED: official docs w32] | high | pending |
| 9 | PreModelSwitch / PostModelSwitch Hooks | New hook events fire before and after model switches; PostModelSwitch can add context for the new model | https://code.claude.com/docs/en/whats-new/2026-w36 | WATCH — [VERIFIED: official docs w36] | high | pending |
| 10 | `maxEffortLevel` Setting | Caps effort level across all providers per model; set at top level or under `modelSettings` | https://code.claude.com/docs/en/whats-new/2026-w37 | WATCH — [VERIFIED: official docs w37] | high | pending |
| 11 | Claude Security Plugin | Multi-agent vulnerability scanner: maps architecture, builds threat model, hunts vulnerabilities, produces patches | https://code.claude.com/docs/en/whats-new/2026-w30 | WATCH — [VERIFIED: official docs w30] | high | pending |
| 12 | Anthropic Scion: Agent-Scale Source Control | Anthropic rebuilt source control after merges/day grew from 2.5k to 30k in a few months; server-side commits, sparse checkouts, immutable content-addressed blobs | https://www.anthropic.com/research/redesigning-source-control | WATCH — [VERIFIED: anthropic.com/research] | high | pending |
| 13 | ProjectMem: Event-Sourced Coding Memory | Local-first MCP server; append-only typed event log (issues, attempts, fixes, decisions); exports gotchas into CLAUDE.md automatically | https://arxiv.org/abs/2606.12329 | TEST — [UNVERIFIED: third-party; pattern extractable, do not install] | medium | pending |
| 14 | MemChain: Trainable Memory Policy | Structured evidence chains (plan → trace → actions) trained with RL; reduces memory context overhead while maintaining retrieval quality | https://arxiv.org/abs/2607.24097 | WATCH — [UNVERIFIED: arxiv only; no implementation] | medium | pending |
| 15 | `promptCacheTtl` Setting (Week 35) | Set 1h cache TTL for main conversation when using an API key or cloud provider; `subagentPromptCacheTtl` for subagents — cost optimization for routine sessions | https://code.claude.com/docs/en/whats-new/2026-w35 | ADOPT — [VERIFIED: official docs w35] | high | pending |

---

## Patterns Worth Knowing

### 1. Plugin Eval Loop: The Missing Quality Gate for Compound-Brain Skills

`claude plugin eval` introduces a principled quality gate that was missing for compound-brain skills.
The pattern: `eval init` has Claude draft test cases by asking "what does a good result look like";
each case tests an intent (did the skill trigger, did it produce the right output, did it NOT over-trigger?);
`eval .` runs the suite against both plugin-on and plugin-off, producing a delta score. This directly
addresses the problem the brain has had no way to measure: whether adding a skill to the plugin
actually improves Claude's output vs. just consuming context budget.

### 2. /skill-doctor as Continuous Context Audit

Every skill in the listing adds to context on every turn, whether used or not. `/skill-doctor` makes
this cost visible per skill, with usage frequency alongside token cost. Combined with `promptCacheTtl`,
this gives a coherent loop: measure cost (skill-doctor), tune TTL to reduce cache misses (promptCacheTtl),
remove unused skills (via eval or skill-doctor output). No new memory system needed — just measurement.

### 3. Cross-Session Messaging as Coordination Primitive

Scheduled routines can now send findings directly to live interactive sessions on the same machine
(and to cloud sessions one-way). For compound-brain, this means: a background research run can
message the user's interactive session when it finds something that needs a decision, rather than
writing to a file and waiting for the next session. The `notify_when_idle` input on `SendMessage`
(w34) handles the case where the recipient session is busy — it notifies when it next goes idle.

### 4. Auto Mode as Default Changes Security Posture

As of August 14, 2026, new sessions on Pro/Max/Team start in auto mode by default. The classifier
handles permission prompts; it blocks destructive git commands, reads outside working dirs, and
credential-fetching from metadata endpoints by default. For scheduled routines, this means auto mode
is active without any explicit setup. The implication: hooks designed to gate permissions may be
partially superseded by the classifier — worth auditing for overlap.

### 5. Anthropic's Scion Insight: Infrastructure Bottlenecks Shift When AI Writes Code

The Scion post documents a pattern that matters architecturally: once code generation becomes cheap,
the limits move to source control, CI, and merge queues designed for human-paced work. Scion's
response — server-side commits, immutable content-addressed objects, optional sparse checkouts,
no global merge-queue locks — is an architecture adapted to agent-scale throughput. The implication
for brain design: if the brain ever runs multiple parallel worktrees or routines, the same patterns
(immutable event log, sparse state, avoid global locks) apply at a smaller scale.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| `claude plugin eval` | compound-brain plugin development | Measure whether each skill helps vs. just costs context; run baseline delta before promoting a candidate-skill draft |
| `/skill-doctor` | Plugin context budget | Audit which of compound-brain's skills are unused in routine sessions; remove dead weight before next run |
| `promptCacheTtl: 1h` | Scheduled routines | Explicit 1h cache TTL reduces cache misses on long-running routines; `subagentPromptCacheTtl` can be lower for short subagents |
| Cross-session messaging | Routine-to-interactive coordination | Background digest run can notify live session when it finds a decision-needed item; replaces write-to-file pattern |
| Concise output style | All routine sessions | `outputStyle: Concise` reduces preamble in routine outputs; makes digest sections easier to parse programmatically |
| ProjectMem event log pattern | .brain/ memory design | Extract the typed event-log pattern (issues/attempts/fixes/decisions) into the brain's daily note schema |
| PreModelSwitch hook | Model governance | Log or block model switches in autonomous sessions where the model must stay predictable |
| `maxEffortLevel` | Routine cost control | Cap effort on routine sessions to prevent an inadvertent `/effort max` from multiplying run cost |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Add queue row 012 and mark it in_progress, then done

**Risk: SAFE** — markdown edit to .brain/queue.md
Applied in this run. ✅ (see queue.md update below)

---

### [SAFE-2] Draft candidate skill: plugin-eval quality gate

**Risk: SAFE** — markdown write under `.brain/candidate-skills/`

Pattern: before promoting a `.brain/candidate-skills/<name>/SKILL.md` to the plugin, run
`claude plugin eval init` from the plugin root to draft test cases, then `claude plugin eval .`
to score with-and-without delta. Only promote when delta is positive.

Draft written to: `.brain/candidate-skills/plugin-eval-pattern/SKILL.md` ✅

---

### [SAFE-3] Update prior digest outcome fields

**Risk: SAFE** — markdown edits to 2026-08-04 digest

The 2026-08-04 digest item #4 (/fork vs /subtask) can be updated:
- **#4 /fork vs /subtask**: Week 33 confirms fork mode is on by default in interactive sessions.
  Outcome: `confirmed — fork mode on by default as of w33; fork = new background session, still correct`

---

### NEEDS APPROVAL (not applied this run)

- **Add `outputStyle: Concise` to routine session settings** — touches `~/.claude/settings.json` or `.claude/settings.json`
- **Add `promptCacheTtl: "1h"` to settings** — same
- **Add `maxEffortLevel` cap for routine sessions** — settings change
- **Audit brain hooks for auto mode overlap** — touches `.claude/hooks/`; also may require no action once audited
- **Run `/skill-doctor` on compound-brain plugin** — read-only audit, but its output may propose skill removals
- **Run `claude plugin eval init` on compound-brain plugin** — drafts test cases; interactive session required; one-time setup
- **ProjectMem event-log export to CLAUDE.md** — do NOT install ProjectMem; pattern is extractable as a native brain update but touches CLAUDE.md content

---

## Recommended Actions

1. **Run `/skill-doctor` on compound-brain in an interactive session.** This is a read-only audit
   that surfaces which skills cost context without being used. Output drives pruning decisions before
   the next plugin eval. Queue item 009 (verify plugin loads in a cloud session) is a prerequisite —
   if the plugin isn't loading, skill-doctor has nothing to measure.

2. **Schedule one `claude plugin eval init` session on compound-brain.** This is the missing quality
   gate for brain skills. Run it interactively (not in a scheduled routine — eval calls are real model
   calls on your account). Let Claude draft 5–7 test cases covering: does the weekly-digest skill
   trigger, does the brain-orient skill produce a useful brief, does the brain-write skill not
   over-trigger on unrelated prompts.

3. **Set `promptCacheTtl: "1h"` for scheduled routine sessions.** Requires approval to touch settings.
   This is a pure cost optimization: the routine's main conversation hits the same context on each
   retry, and a 1h TTL keeps it warm through the entire run. Prioritize after queue item 009 is verified.

---

## Needs Approval

- **Queue 006**: Delete branch `claude/cool-heisenberg-2iokix` — owner action, outward-facing
- **Queue 007**: Switch repo visibility to private — owner decision
- **Queue 008**: Run `/doctor` audit — applies CLAUDE.md fixes on confirmation
- **Queue 009**: Verify plugin loads in cloud session — interactive test needed
- **Settings changes**: `outputStyle`, `promptCacheTtl`, `maxEffortLevel` for routine sessions
- **Hook audit**: auto mode default may overlap with existing hook permission gates; audit before modifying
- **Queue 002**: Apply CLAUDE.md hierarchical split proposal — touches root CLAUDE.md and core/BRAIN.md
