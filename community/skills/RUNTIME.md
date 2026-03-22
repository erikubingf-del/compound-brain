# Skill Runtime Integration

This document explains how compound-brain's session-start and cron events
auto-discover, audit, and refresh skills for any activated repo — regardless
of stack, language, or domain.

## The generic loop

```
session-start fires (any repo)
       │
       ▼
skill-gap-detector evaluator          ← community/evaluators/skill-gap-detector.md
       │  reads project signals:
       │  file extensions, deps, languages, CLAUDE.md goals
       │
       ├── scores all available skills against signals
       │   (reads each skill's ## Trigger Signals)
       │
       ├── skill score > 0 AND not active → add to recommended[], notify human
       └── all active skills fresh → pass, silent

daily cron fires (any repo)
       │
       ▼
skill-gap-detector evaluator (with HTTP)
       │
       ├── fetches skill-discovery-sources pack  ← community/source-packs/skill-discovery-sources.md
       │   (GitHub skill registries + stack-specific refs)
       │
       ├── scores newly discovered skills against project signals
       │
       ├── new match found → propose via promotion inbox
       ├── existing skill stale → fetch source, propose refresh via promotion inbox
       └── no changes → update cache timestamp, silent
```

## What makes a skill auto-detectable

Every skill in `community/skills/` MUST have a `## Trigger Signals` section
in its `SKILL.md`. This is what the generic evaluator reads — no hardcoded
skill names, no per-project configuration.

Good trigger signals are concrete and observable:
```markdown
## Trigger Signals
- `ext:tsx` or `ext:jsx` present in project
- `dep:react` or `dep:next` in package.json
- User request contains "design", "UI", "component"
```

Bad trigger signals are vague or require LLM judgment:
```markdown
## Trigger Signals
- Project seems to have a frontend
- User appears to be building a website
```

The evaluator does string matching, not LLM inference. Keep signals specific.

## Session start vs cron budget

| Event | Budget | Allowed |
|-------|--------|---------|
| Session start | 10s | File scan, skills.json read, signal scoring only |
| Cron | 60s | Above + HTTP fetches from source pack |

Session start must never block the human. HTTP and LLM calls are cron-only.

## Promotion flow (how a new skill reaches a repo)

1. Cron finds a new skill from `skill-discovery-sources` with score ≥ 2
2. Writes candidate to `~/.claude/knowledge/promotions/inbox.md`
3. Human reviews: skill name, trigger match explanation, source URL
4. Human approves → `apply_approved_promotions.py` installs skill
5. On next session start, evaluator finds it in skill dirs and marks active

The human is always in the loop before `active[]` changes.

## Skill freshness

A skill becomes stale when:
- Its source pack has a newer version of a referenced guideline
- A dependency it covers has had a major version bump
- The skill's `## Approved Sources` URLs return different content than cached

Staleness triggers a proposed diff in the promotion inbox, not an auto-update.

## How to write a skill with good runtime integration

1. `SKILL.md` — the instructions the LLM follows (what to do)
2. `## Trigger Signals` — specific, observable signals the evaluator can match
3. `## Compatibility` — which tools and install paths support this skill
4. Optional: submit a matching source pack to `community/source-packs/`
   if your skill has external references that can go stale

That's it. The generic evaluator handles the rest. No per-skill evaluator
needed unless the skill has non-standard detection logic.

## ui-master as a worked example

`community/skills/ui-master/SKILL.md` shows this pattern in practice:
- Trigger signals: `ext:tsx`, `ext:jsx`, `dep:tailwindcss`, `dep:react`
- Source pack: `ui-master-sources` (now removed — covered by skill-discovery-sources)
- The evaluator would score it highly on any Next.js/React repo without being
  told anything about UI — purely from file and dep signals
