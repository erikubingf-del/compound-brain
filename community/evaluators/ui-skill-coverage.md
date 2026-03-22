# Evaluator Submission

## Name

`ui-skill-coverage` — UI Skill Gap and Freshness Evaluator

## Repo Type

Any repo with `.tsx`, `.jsx`, `.html`, `.css`, `tailwind.config.*`, or
UI framework dependencies (`react`, `next`, `vue`, `svelte`, `@shadcn/ui`).

## Objective

On session start and cron, detect whether the repo needs the `ui-master` skill
and whether the installed skill is fresh. Produces a pass/flag/missing signal
that the runtime uses to recommend or refresh the skill.

This evaluator never modifies the skill or the repo directly.
It only emits a signal. The runtime governs what happens next.

## Run Command

```bash
python3 ~/.claude/scripts/evaluate_skill_coverage.py \
  --skill ui-master \
  --source-pack ui-master-sources \
  --project-dir . \
  --stale-days 30
```

If the script is not yet present, the evaluator can be approximated inline:

```bash
# Step 1 — detect UI signals
UI_SIGNALS=$(find . -maxdepth 4 \
  \( -name "*.tsx" -o -name "*.jsx" -o -name "tailwind.config.*" \) \
  -not -path "*/node_modules/*" | wc -l | tr -d ' ')

# Step 2 — check skill state
SKILL_STATUS=$(python3 -c "
import json, sys, os
p = '.brain/state/skills.json'
if not os.path.exists(p):
    print('missing')
    sys.exit()
data = json.load(open(p))
skills = data.get('active', []) + data.get('recommended', [])
names = [s.get('name','') if isinstance(s,dict) else str(s) for s in skills]
print('active' if 'ui-master' in names else 'missing')
" 2>/dev/null || echo "missing")

echo "ui_signals=$UI_SIGNALS skill_status=$SKILL_STATUS"
```

## Metric Extraction Rule

From the run output, extract:
- `ui_signals` — integer count of UI-related files found
- `skill_status` — one of: `active`, `stale`, `missing`
- `source_pack_age_days` — days since `ui-master-sources` was last fetched
  (read from `.brain/state/source-pack-cache.json` if present)

## Keep or Discard Rule

| Condition | Signal | Runtime action |
|-----------|--------|---------------|
| `ui_signals == 0` | `skip` | Repo has no UI — do not recommend skill |
| `ui_signals > 0` AND `skill_status == active` AND `source_pack_age_days < 30` | `pass` | Skill present and fresh — no action |
| `ui_signals > 0` AND `skill_status == active` AND `source_pack_age_days >= 30` | `stale` | Fetch source pack, propose diff via promotion inbox |
| `ui_signals > 0` AND `skill_status == missing` | `missing` | Add `ui-master` to `.brain/state/skills.json` recommended list, surface to human |
| Any source pack URL returning non-200 | `warn` | Log to `.brain/knowledge/areas/skill-health.md`, do not block session |

## Mutable Surfaces

- `.brain/state/skills.json` — `recommended` array only (never `active` without approval)
- `.brain/state/source-pack-cache.json` — last-fetched timestamps
- `.brain/knowledge/areas/skill-health.md` — warning log

## Protected Surfaces

- `~/.claude/skills/ui-master/SKILL.md` — never auto-modified
- `.brain/state/skills.json` `active` array — human approval required to add/remove
- Any project source files — this evaluator is read-only on project code

## Runtime Budget

- Max 10 seconds on session start (file scan + JSON read only)
- Max 30 seconds on cron (includes source pack HTTP fetches)
- If budget exceeded, emit `timeout` signal and skip — never block the session

## Failure Classes

- **Missing `.brain/`** — skip evaluator, do not scaffold (that is activation's job)
- **Malformed `skills.json`** — log warning to skill-health.md, continue
- **Source pack HTTP failure** — log to skill-health.md, mark cache as stale, continue
- **Script not found** — fall back to inline bash approximation above

## Evidence

- CRM repo (`/Users/erikfigueiredo/crm`) — 200+ `.tsx` files, `tailwindcss` dep,
  `ui-master` installed after manual audit. This evaluator would have surfaced
  the gap automatically on first session start.
- Source pack fetch caught Vercel guidelines URL change from `/command.md` to
  updated path — prevented skill from referencing a dead URL.
