# Getting Started with compound-brain

This guide explains what happens after you run `install.sh` and activate your
first repo. It answers the three questions that trip up most new users:

1. How do departments actually work?
2. What does autonomy-depth mean in practice?
3. Where does knowledge go — global vs per-repo vs state?

---

## What activation gives you

After running `activate_repo.py` on your repo, four things are live:

```
your-repo/
├── CLAUDE.md                        ← instructions loaded by Claude Code / Codex
├── .brain/
│   ├── memory/
│   │   ├── project_context.md       ← goal, stack, current state (edit this)
│   │   └── feedback_rules.md        ← how you want the AI to behave
│   ├── knowledge/                   ← PARA knowledge for this repo (git-track)
│   │   ├── projects/, areas/, resources/, qmp/, decisions/, skills/
│   │   └── daily/, weekly/          ← session logs (.gitignore these)
│   └── state/                       ← runtime files (.gitignore these)
│       ├── skills.json              ← active, recommended, missing skills
│       ├── autonomy-depth.json      ← current depth + trust score
│       ├── operator-recommendation.json ← what should happen next and why
│       └── departments/             ← per-dept action state
└── .claude/
    ├── departments/                 ← dept contracts (owned surfaces, allowed actions)
    ├── hooks/                       ← session-start, stop, cron wiring
    └── settings.local.json          ← tool permissions
```

---

## How departments work

Departments are the governance layer. They decide what the AI is allowed to do
autonomously, and gate changes that affect their surfaces.

**Default departments:**
- `architecture` — owns structural decisions, gates control-plane changes
- `engineering` — owns implementation, tests, deps
- `product` — owns user-facing features, copy, UX
- `research` — owns experiments, evaluations, external references

**A concrete cycle (what happens on session-start at depth 3):**

```
1. SessionStart hook fires
2. Runtime reads .brain/state/action-queue.md
   (probability engine ranked: bug-fix P1, test-coverage P2, refactor P3)
   and writes .brain/state/operator-recommendation.json
   (lead department, blocked approvals, trust score, next bounded move)

3. Engineering dept is the lead for P1 (bug-fix)
   → Engineering reads its contract: .claude/departments/engineering.md
   → Engineering checks: is this action in my allowed list? yes
   → Engineering proposes action to .brain/state/department-agreement.json

4. Architecture reviews the proposal
   → Is this a control-plane change? no → agrees
   → No other dept objects

5. Action executes (bounded: one action, one cycle)
6. Result logged to .brain/knowledge/daily/YYYY-MM-DD.md

7. If architecture had objected:
   → Depth does not drop, but action is blocked
   → Human sees the objection in the next session-start summary
   → Human resolves by editing .brain/state/approval-state.json or dept contract
```

**The key rule:** one lead department owns the action. Supporting departments
can agree, agree with constraints, or object. Operations and architecture
objections are hard blocks. Product and research objections are soft signals.

**To change what a dept owns or allows:**
Edit `.claude/departments/<department>.md`. Strategic changes go through an
approval (written to `.brain/state/approval-state.json`).

---

## What autonomy-depth means

Depth is a number from 0 to 5. It controls how much the runtime does on its own.

| Depth | What the runtime can do |
|-------|------------------------|
| 0 | Preview only — reads repo, writes nothing |
| 1 | Memory only — writes `.brain/` knowledge, no execution |
| 2 | Bounded planning — can propose actions, no execution |
| 3 | Bounded execution — can execute approved actions per dept cycle |
| 4 | Evaluator-backed experiments — can run autoresearch with fixed evaluator |
| 5 | High autonomy — broader execution within approved surfaces |

**Trust score** controls when depth raises or lowers:

```
Trust score = weighted sum of:
  - recent approval compliance (did you approve suggested actions?)
  - healthy streak (consecutive days with no failures)
  - skill coverage (are the right skills active for this repo's stack?)
  - dept agreement rate (are depts aligned, or always objecting?)
  - heartbeat health (is cron running without failures?)
```

Depth rises when trust score clears the raise threshold for your current depth.
Depth drops when approvals are pending too long, cron fails repeatedly, or an
architecture objection is unresolved.

**To see current status:**
```bash
cat .brain/state/autonomy-depth.json
cat .brain/state/runtime-governor.json
cat .brain/state/operator-recommendation.json
```

**Most repos should start at depth 2, reach depth 3 within a week of normal
use, and stay there.** Depth 4+ requires autoresearch enablement and a validated
evaluator contract — you explicitly enable this, it does not happen automatically.

---

## Where knowledge goes

Three locations, three purposes:

```
~/.claude/knowledge/      GLOBAL — cross-project patterns
                          Put here: QMP entries that apply to any repo,
                          skills you want everywhere, decisions that set
                          cross-project rules

<repo>/.brain/knowledge/  PER-REPO — project-specific knowledge
                          Put here: this repo's project notes, decisions,
                          daily logs, skills, QMP patterns specific to
                          this domain

<repo>/.brain/state/      RUNTIME STATE — not knowledge
                          This is machine-written. Do not edit directly.
                          It tracks: depth, trust, dept state, skill cache
```

**Git tracking guide:**

```
# Track (shared with team)
.brain/knowledge/projects/
.brain/knowledge/areas/
.brain/knowledge/resources/
.brain/knowledge/qmp/
.brain/knowledge/decisions/
.brain/knowledge/skills/
.brain/memory/project_context.md
.brain/memory/feedback_rules.md
CLAUDE.md
.claude/departments/

# Do not track (machine state + local session logs)
.brain/state/
.brain/knowledge/daily/
.brain/knowledge/weekly/
.brain/memory/project_context_cache.*
```

**Promotion to global:**

When you discover a pattern that applies to more than one repo:

```
1. Document it in .brain/knowledge/qmp/ or resources/
2. Submit to the global promotion inbox:
   ~/.claude/knowledge/promotions/inbox.md
3. The scheduled review loop evaluates it
4. If approved: python3 ~/.claude/scripts/apply_approved_promotions.py
5. Pattern is now in ~/.claude/knowledge/ and available to all your repos
```

---

## Skills

Skills are discovered automatically — you do not configure them per repo.

On every session start, the `skill-gap-detector` evaluator reads your project's
file extensions and package dependencies, scores every available skill against
those signals, and adds good matches to `.brain/state/skills.json` recommended
list. You approve, and the skill becomes active.

On daily cron, the evaluator also fetches the `skill-discovery-sources` pack
to find new skills from external registries and stack-specific references.

**To see what skills are active or recommended:**
```bash
cat .brain/state/skills.json
```

**To add a new skill globally (personal, not community):**
```bash
# Create the skill
mkdir ~/.claude/skills/my-skill
# Write SKILL.md with ## Trigger Signals section
# The evaluator will auto-detect and recommend it for matching repos
```

**To share a skill with your team:** see [`community/skills/SHARING.md`](community/skills/SHARING.md)

**To contribute a skill to the community:** see [`community/skills/README.md`](community/skills/README.md)

---

## A day in the life of an activated repo

Once your repo is activated, this is the full loop that runs without you:

```
MORNING — session open
────────────────────────────────────────────────
SessionStart hook fires
  → project_session_start.py dispatches session-start event
  → runtime reads .brain/state/ (depth, trust, approvals, skills, dept state)
  → skill-gap-detector runs (10s, file scan only)
    → new skill match → added to recommended[], you get notified
  → probability engine ranks the action queue
    → P1: bug-fix (0.87)  P2: test-coverage (0.71)  P3: refactor (0.44)
  → lead department determined from top action (Engineering for P1)
  → operator brief written to .brain/state/operator-recommendation.json:
      lead: engineering
      action: fix null-check in payments module
      trust: 74  depth: 3  blocked: none
      recommended move: bounded execution, one action, verify after

Claude wakes and reads the brief instead of starting from scratch.
You see: what matters now, which dept is active, what is blocked, what to do next.

DURING THE SESSION
────────────────────────────────────────────────
Engineering dept leads the P1 action
  → checks its contract: .claude/departments/engineering.md
  → checks approval-state.json — no strategic gate blocking this
  → proposes action to department-agreement.json
  → Architecture reviews: is this a control-plane change? no → agrees
  → Action executes (one bounded step)
  → Result logged to .brain/knowledge/daily/YYYY-MM-DD.md

If a reusable pattern emerged:
  → QMP entry added to .brain/knowledge/qmp/
  → .brain/knowledge/skills/skill-graph.md updated if capability changed
  → .brain/knowledge/decisions/log.md updated if strategic choice was made

SESSION END
────────────────────────────────────────────────
Stop hook fires
  → project_stop.py dispatches stop event
  → session compressed: daily note updated, project state updated
  → trust score recalculated from: approvals, healthy streak,
    dept agreement rate, skill coverage, heartbeat health
  → depth governor checks thresholds:
      trust 74 → stays at depth 3 (raise threshold is 75)
      one more clean session → depth rises to 4

BETWEEN SESSIONS — cron heartbeat
────────────────────────────────────────────────
project_llm_cron.py fires (configured interval, default daily)
  → at depth 2: planning only — refreshes audit, updates brief, no execution
  → at depth 3: bounded department cycle — Engineering runs P1 if not done
  → at depth 4+: evaluator-backed autoresearch may run if program.md exists

Global skill radar cron fires (weekly)
  → searches approved GitHub patterns by dept + capability
  → extracts project tips from activated repos
  → writes ~/.claude/knowledge/resources/skill-catalog.json
  → next session-start surfaces relevant new skills to your repo

Global promotion review fires (scheduled)
  → reads ~/.claude/knowledge/promotions/inbox.md
  → reviews cross-project candidates
  → approved patterns written into ~/.claude/knowledge/ for all repos

AFTER A WEEK
────────────────────────────────────────────────
.brain/knowledge/decisions/log.md  — every strategic choice recorded
.brain/knowledge/daily/            — full session trail
.brain/knowledge/skills/           — capability map for this repo
.brain/state/autonomy-depth.json   — depth and trust score trend
~/.claude/knowledge/               — patterns that transferred across repos

The repo knows its own history. The next session starts from evidence,
not from a blank context.
```

**The key invariant:** every session leaves `.brain/` more useful than before.
Hooks handle session boundaries. Cron keeps the repo moving between them.
The probability engine decides what to do next. Departments govern who can do it.
Memory makes every session faster than the last.

---

## Common operations

| Goal | Command |
|------|---------|
| Check repo activation state | `python3 ~/.claude/scripts/activate_repo.py --project-dir . --check-only` |
| See current depth + trust | `cat .brain/state/autonomy-depth.json` |
| See active/recommended skills | `cat .brain/state/skills.json` |
| See pending approvals | `cat .brain/state/approval-state.json` |
| See dept agreement state | `cat .brain/state/department-agreement.json` |
| Promote a pattern to global | Add entry to `~/.claude/knowledge/promotions/inbox.md` |
| Apply approved promotions | `python3 ~/.claude/scripts/apply_approved_promotions.py` |
| Run watchdog manually | `python3 ~/.claude/scripts/runtime_watchdog.py` |

---

## What to do before and after activation

### Before running activate_repo.py (do this first)

Write `.brain/memory/project_context.md` before activating. This is the single
most important step — it tells the runtime what the repo actually is, prevents
any cross-repo goal inference, and gives every future session the right context
from day one.

Minimum viable `project_context.md`:

```markdown
# Project Context — your-repo-name

## Goal
One sentence: what this repo ships and for whom.

## Stack
Languages, frameworks, databases, infra.

## Domain
What kind of product/service this is (SaaS, API, ML system, CLI, etc.)

## Hard Rules
Non-negotiable constraints the AI must follow in this repo.
```

Then run:

```bash
# Step 1 — prepare (writes .brain/ scaffold)
python3 ~/.claude/scripts/prepare_brain.py /path/to/repo

# Step 2 — write project_context.md NOW, before activate
# (your goal will be used directly — no inference, no bleed)

# Step 3 — activate
python3 ~/.claude/scripts/activate_repo.py --project-dir /path/to/repo
```

### After activation

1. Edit `.brain/memory/feedback_rules.md` — how you want the AI to behave
2. Open the repo in Claude Code or Codex — session-start hook fires, skills scored
3. Approve or reject skill recommendations in `.brain/state/skills.json`
4. Watch the first department cycle — check `.brain/knowledge/daily/` for the log

That is the full loop. Everything else is the same pattern at larger scale.
