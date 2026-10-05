# LLM Architecture Digest: 2026-10-05

schema_version: "1.0"
required_sections: [top_finds, patterns, upgrade_opportunities, auto_apply_queue, recommended_actions, needs_approval]

**Run scope:** 4-lane research scan covering weeks w33–w40 (August 10 – October 5, 2026) plus
new Anthropic engineering blog posts and community/research sources since the last run
(2026-08-04). All items in prior digests (w27–w32, August 2026 and earlier) are excluded.

---

## Top Finds

| # | Name | Description | URL | Classification | Confidence | Outcome |
|---|------|-------------|-----|----------------|-----------|---------|
| 1 | Claude Code Mods | Plugins can now act as session middleware: rewrite prompts, block/retry tool calls, approve/deny permissions, strip secrets, and draw custom UI (buttons, panels, /commands). Install via `/plugin`. Requires v2.1.287+. | https://code.claude.com/docs/en/whats-new (early Oct 2026) | ADOPT — [VERIFIED: official docs / AI Daily Digest Oct 3 2026] | high | pending |
| 2 | `claude plugin eval` | Test your plugin against a suite of realistic prompts + graders (regex, tool-call checks, rubric model). Baseline compares with no-plugin. `init` subcommand generates cases automatically. | https://code.claude.com/docs/en/plugin-evals | ADOPT — [VERIFIED: official docs w37] | high | pending |
| 3 | Projects Beta: Coordinator + Parallel Cloud Sessions | A coordinator session delegates goals to parallel cloud sessions; no manual subagent spawning needed. Alpha as of Sep 2026. | https://code.claude.com/docs/en/whats-new (Sep 2026) | ADOPT — [VERIFIED: official docs] | high | pending |
| 4 | `maxEffortLevel` per Provider | New top-level and per-model `maxEffortLevel` setting caps effort on every provider (Bedrock, Google Cloud Agent Platform, Microsoft Foundry). Budget ceiling for autonomous sessions. | https://code.claude.com/docs/en/whats-new/2026-w37 | ADOPT — [VERIFIED: official docs w37] | high | pending |
| 5 | Managed Agents — Brain/Hands Decoupling | Anthropic's hosted agent harness (launch: Apr 8 2026). Brain (model+harness) decoupled from hands (sandbox+tools) — each evolves independently. Stateless cattle, not monolithic pets. Early adopters report 10x faster deployment. | https://www.anthropic.com/engineering/managed-agents | ADOPT — [VERIFIED: official Anthropic engineering blog] | high | pending |
| 6 | Opus 5.5 Default + Pro/Team on Opus | Sep 22 2026: Opus 5.5 became default Opus model; Pro and Team Standard switched from Sonnet to Opus. Affects session budget and context calculations for all cloud-mode sessions. | https://code.claude.com/docs/en/whats-new (Sep 2026) | WATCH — [VERIFIED: official docs] | high | pending |
| 7 | Background Subagent Command Limit Removed | September 2026 removed the 1-hour cap on background commands started by subagents. Long-running data processing or research lanes no longer time out. | https://code.claude.com/docs/en/whats-new (Sep 2026) | WATCH — [VERIFIED: official docs] | high | pending |
| 8 | Fork Mode On by Default (w33) | Fork mode is now the default orchestration path; the prior default (in-session fork) now requires explicit `/subtask`. Affects any session that relied on the old `/fork` default. | https://code.claude.com/docs/en/whats-new/2026-w33 | WATCH — [VERIFIED: official docs w33] | high | pending |
| 9 | GitLab MR Integration + Marketplace (w33) | GitLab merge requests and a GitLab plugin marketplace now join GitHub in Claude Code's supported integration surface. | https://code.claude.com/docs/en/whats-new/2026-w33 | WATCH — [VERIFIED: official docs w33] | medium | pending |
| 10 | Cache Miss Diagnostic Hints | Claude Code now reports the likely cause of a cache miss (changed tool definitions, system prompt change, expiry after idle). Reduces debug time for autonomous routines that depend on caching. | https://code.claude.com/docs/en/whats-new (Sep 2026) | WATCH — [VERIFIED: official docs] | high | pending |
| 11 | SSGM: Stability + Safety Governed Memory | Research framework (arXiv 2603.11768, Mar 2026): pre-consolidation validation, temporal/provenance grounding, access-scoped retrieval, and reversible reconciliation compose into one memory governance lifecycle. Addresses poisoning, semantic drift, hallucination-at-retrieval. | https://arxiv.org/abs/2603.11768v1 | TEST — [UNVERIFIED: research paper; patterns extractable, no third-party code] | medium | pending |
| 12 | Superpowers Community Plugin (Official Marketplace) | 280k-star composable SDLC skills framework by Jesse Vincent. Accepted into Anthropic's official marketplace Jan 2026. Install: `/plugin install superpowers@claude-plugins-official`. Chains brainstorming → worktree → plan → TDD → review. | https://www.anthropic.com (official marketplace listing) | TEST — [VERIFIED: official marketplace; skills content is third-party, extract patterns before enabling broadly] | high | pending |
| 13 | C Compiler Multi-Agent Architecture Patterns | Anthropic Feb 2026 experiment: 16 parallel agents built a 100k-line Rust C compiler capable of compiling Linux 6.9. Pattern: lock-file task claiming, isolated Docker containers, shared Git repo. Zero human edits during run. | https://www.anthropic.com/engineering/building-c-compiler | WATCH — [VERIFIED: official Anthropic engineering blog] | high | pending |
| 14 | In-Process Retrieval as Extended Working Memory | arXiv 2607.05690 (Jul 2026): retrieval injected into the live context window mid-execution ("memory in the loop") rather than pre-loaded or post-processed. Bridges working memory limitations for long-horizon tasks. | https://arxiv.org/pdf/2607.05690 | TEST — [UNVERIFIED: research paper; pattern extractable] | medium | pending |
| 15 | /design Skill + Concise Output Style (w34) | `/design` skill drafts editable UI artboards within Claude Code Desktop. Separate addition: Concise output style setting reduces verbosity in sessions where brevity matters. | https://code.claude.com/docs/en/whats-new/2026-w34 | WATCH — [VERIFIED: official docs w34] | medium | pending |

---

## Patterns Worth Knowing

### 1. Mods as Session Middleware Layer

Claude Code Mods introduce a new architectural layer between the user's prompt and the
model's execution: a plugin can now intercept, rewrite, or block at the prompt and tool
levels before anything reaches Claude. This changes the trust model for compound-brain's
autonomous sessions. A mod could: strip secrets from tool output before they land in
context, block outbound writes outside `.brain/**` as a safety rail, or rewrite a
cron-fired prompt to include fresh runtime state automatically. The middleware pattern
is more reliable than a CLAUDE.md instruction because it fires deterministically at the
tool boundary — it is a code enforcement, not an instruction.

### 2. Brain/Hands Decoupling as a Design Principle

Anthropic's Managed Agents paper formalizes what compound-brain already does informally:
separate what reasons (the model + harness) from what executes (tools + sandbox) and what
persists (sessions + `.brain/` state). The key upgrade is treating each layer as a
replaceable Lego brick with a versioned interface. Concretely for this repo: the brain's
state contract (the `.brain/state/` JSON files) is the interface — departments and hooks
depend on it, not on each other. When a model upgrade changes reasoning behavior, only
the harness adapter needs updating; the state files don't move.

### 3. `claude plugin eval` Closes the Skill Validation Loop

Prior skill quality relied on manual review or human use. Plugin eval runs a skill
against automatically generated test cases and compares to a no-skill baseline, producing
a measurable delta. This pairs naturally with the candidate-skills directory: a candidate
skill earns promotion when it passes its eval suite. The validate-digest skill (queue 003)
could be rewritten as a plugin eval spec rather than a markdown contract, making the
validation machine-checkable instead of prose.

### 4. Projects (Coordinator + Parallel Sessions) as Native Ralph Loop

The Projects beta exposes the Ralph Loop pattern as a first-party feature: a coordinator
session holds the spec and delegates bounded tasks to parallel cloud sessions, each of
which starts with fresh context. This is the same architecture as the C compiler
experiment (lock-file claiming + isolated contexts + shared state), now available without
Docker or manual orchestration. For compound-brain, Projects is the upgrade path from
the current single-session weekly digest to a parallel multi-lane research run.

### 5. SSGM Extends SAGE from Novelty to Governance

The SAGE novelty gate (queue 005) addresses write-side cost: skip redundant writes.
SSGM addresses write-side safety: prevent poisoned, drifted, or hallucinated memory from
consolidating. The two compose naturally: SAGE filters for novelty first (cheap), SSGM
validates before consolidation (more expensive but scoped to non-redundant writes only).
Together they form a complete write-side memory controller.

---

## Brain Upgrade Opportunities

| Pattern | Which Brain Component | Expected Benefit |
|---------|----------------------|-----------------|
| Mods middleware | Autonomous sessions | Deterministic write-gate (block `.brain/**` writes that weren't produced by an approved routine); secret strip from tool output before context; no-code enforcement of SAFE boundary |
| `claude plugin eval` | Candidate skills review | Add eval spec to each candidate skill; automated promotion gate replaces manual review |
| Projects beta | Weekly digest routine | Replace sequential search with parallel coordinated cloud sessions; coordinator synthesizes; 4x research throughput |
| Brain/hands decoupling (state contract) | `.brain/state/` schema | Formalize the state JSON files as a versioned interface; departments reference the schema, not each other |
| SSGM + SAGE composition | Memory write path | SAGE novelty filter (queue 005) + SSGM validation before consolidation = complete write-side memory controller |
| Opus 5.5 default | CLAUDE.md budget rule | Prior context budget rule assumed Sonnet model; Opus 5.5 as default may change token-per-request cost; revisit whether 5% of 1M tokens is still the right threshold |
| Remove background time cap | Long-horizon routines | Multi-hour research or autoresearch runs are now safe to launch as background subagents without a timeout safety net |
| C compiler lock-file claiming | Multi-agent coordination | Pattern: flat lock files in the repo; an agent checks lock before starting a task, writes lock on claim, deletes on done — no broker needed |

---

## AUTO-APPLY QUEUE

### [SAFE-1] Add Queue Row for This Run

**Risk: SAFE** — markdown edit to `.brain/queue.md`

Add row 012: `weekly digest 2026-10-05 | done | medium | weekly-digest`.
Applied below in Step 5.

---

### [SAFE-2] Note Mods Middleware as Candidate Write-Gate

**Risk: SAFE** — draft markdown under `.brain/candidate-skills/`

Draft `.brain/candidate-skills/brain-write-gate-mod/SKILL.md` describing a mod that
intercepts Write/Edit/Bash tool calls and blocks any path outside `.brain/**` during
unattended runs. This is the deterministic enforcement layer that CLAUDE.md instructions
cannot reliably provide. Drafting is SAFE; enabling a mod in a live session is NEEDS APPROVAL.

---

### [SAFE-3] Update Prior Digest Outcome Fields

**Risk: SAFE** — markdown edit under `.brain/knowledge/research/`

2026-08-04 items with `outcome: pending` that can be updated based on what this session
knows:
- Item 6 (Anti-Fabrication notifications): `confirmed` (this scheduled run received the
  anti-fabrication notice language — it works as documented)
- All others: remain `pending` (no evidence of implementation or invalidation since Aug 4)

---

### [SAFE-4] Update AGENTS.md and queue.md

**Risk: SAFE** — markdown appends
Applied below in Step 5.

---

### NEEDS APPROVAL (not implemented this run)

- **Enabling any Mod** — a mod touching sessions requires approval; a write-gate mod is
  architecturally significant
- **Installing Superpowers plugin** — `/plugin install superpowers@claude-plugins-official`
  is outward-facing; skills content comes from a third party and loads in every session
  where compound-brain plugin is enabled
- **Projects beta opt-in** — coordinator + parallel sessions is a new execution model;
  first run should be attended
- **Updating `.claude/settings.json` for `maxEffortLevel`** — settings file change

---

## Recommended Actions

1. **Draft a brain-write-gate Mod spec (SAFE now, enable with approval).** The Mods
   middleware layer can enforce the SAFE/NEEDS-APPROVAL boundary deterministically —
   no instruction can be rewritten by an unattended session if the mod blocks Write/Edit
   calls outside `.brain/**`. Draft the spec in `candidate-skills/`; bring it to a
   human review session to enable.

2. **Test `claude plugin eval` on the existing validate-digest skill (queue 003).** Run
   `claude plugin eval init` against the compound-brain plugin with the digest schema as
   the expected output. This converts the prose contract into a machine-checkable test
   suite and validates the skill actually works in a live session. First attended run only.

3. **Plan a Projects beta attended run for next week's digest.** Projects (coordinator +
   parallel cloud sessions) maps directly onto the weekly digest's 4-lane search. Run
   once in attended mode to verify coordinator handoff and state persistence before
   enabling in the scheduled routine.

---

## Needs Approval

- Enable brain-write-gate Mod (candidate spec can be drafted SAFE; activation requires approval)
- Install Superpowers plugin via official marketplace
- Opt into Projects beta for weekly digest routine
- Set `maxEffortLevel` in `.claude/settings.json` for cron sessions
- Any Mods that rewrite prompts or block tool calls in live sessions
- Queue items 006 (delete public branch), 007 (repo visibility → private), 009 (verify plugin loads), 010 (delete `.claude/skills/`)
