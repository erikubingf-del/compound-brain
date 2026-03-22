# ui-master — Runtime Integration

This document explains how `ui-master` integrates with compound-brain's
session-start, stop, and cron events. The skill itself (`SKILL.md`) is
passive instructions. The runtime integration is what makes it self-auditing
and self-improving.

## How it fits together

```
session-start / cron
       │
       ▼
ui-skill-coverage evaluator         ← community/evaluators/ui-skill-coverage.md
       │
       ├── no UI signals → skip
       ├── skill missing → add to recommended[], surface to human
       ├── skill stale   → fetch ui-master-sources, propose diff via promotion inbox
       └── skill fresh   → pass, no action
                                     ↑
                        ui-master-sources source pack
                        community/source-packs/ui-master-sources.md
                        (Vercel guidelines, shadcn, Radix, WCAG)
```

## Session start behavior

When `project_session_start.py` fires, the shared runtime engine:

1. Reads `.brain/state/skills.json`
2. Runs `ui-skill-coverage` evaluator (budget: 10s, file scan only)
3. If result is `missing` — appends `ui-master` to `recommended[]` in skills.json
   and prints a one-line notice: _"ui-master skill recommended for this repo — run
   `/gsd:add-skill ui-master` to activate"_
4. If result is `stale` — defers source pack fetch to cron (not session start)
5. If result is `pass` or `skip` — silent, no output

Session start must never block or slow down the human. The evaluator is
file-scan only at session start. HTTP fetches only happen in cron.

## Cron behavior

When `project_llm_cron.py` fires (default: daily):

1. Runs `ui-skill-coverage` evaluator (budget: 30s, includes HTTP)
2. Fetches each URL in `ui-master-sources` source pack
3. Compares fetched content against current `SKILL.md` content
4. If differences found:
   - Writes a candidate diff to `~/.claude/knowledge/promotions/inbox.md`
   - Logs to `.brain/knowledge/areas/skill-health.md`
   - Does NOT modify the skill — human reviews via promotion inbox
5. Updates `.brain/state/source-pack-cache.json` with fetch timestamps

## Promotion flow

When a source pack fetch finds a material change (e.g., new WCAG rule, Vercel
guideline update, deprecated API in Motion library):

1. Cron writes a promotion candidate:
   ```
   ~/.claude/knowledge/promotions/inbox.md
   ```
   Entry includes: skill name, source URL, what changed, suggested skill diff

2. Human reviews and approves or rejects

3. On approval:
   ```bash
   python3 ~/.claude/scripts/apply_approved_promotions.py
   ```
   This applies the diff to the canonical skill file.

4. Updated skill propagates to all repos on next session start via the active
   skill state.

## Activation

To activate full runtime integration for a repo:

```bash
# 1. Mark skill as active for this repo
python3 -c "
import json
p = '.brain/state/skills.json'
data = json.load(open(p))
if 'ui-master' not in [s if isinstance(s,str) else s.get('name') for s in data.get('active',[])]:
    data.setdefault('active', []).append({'name': 'ui-master', 'source': 'community', 'activated': '$(date +%Y-%m-%d)'})
json.dump(data, open(p,'w'), indent=2)
print('ui-master activated')
"

# 2. Register evaluator in autoresearch program (if autoresearch is enabled)
# Add to .brain/autoresearch/program.md:
#   evaluator: ui-skill-coverage
#   schedule: session-start + daily-cron
```

## What this does NOT do

- Does not auto-install the skill without human approval
- Does not modify project source files
- Does not run LLM calls on session start (evaluator is script-only)
- Does not replace the human's aesthetic judgment — it only keeps the
  technical rules current
