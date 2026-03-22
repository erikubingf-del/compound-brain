# compound-brain — Project Brain

## What is this project
compound-brain project

---

## Project Brain Location
All project-specific knowledge lives in `.brain/`:

```
.brain/
├── MEMORY.md                        ← memory index
├── memory/                          ← Claude memory files
└── knowledge/
    ├── _index.md
    ├── daily/YYYY-MM-DD.md
    ├── weekly/YYYY-MM-DD.md
    ├── projects/
    ├── areas/
    ├── resources/
    ├── archives/
    ├── skills/skill-graph.md
    ├── qmp/
    ├── decisions/log.md
    └── crons/crons.md
```

**OVERRIDE:** Use `.brain/knowledge/` as the knowledge base for this project.
**OVERRIDE:** Use `.brain/memory/` as the memory base for this project.
Do NOT write project-specific knowledge to `~/.claude/knowledge/` — that is for cross-project patterns only.

---

## Session Workflow

### 1. Retrieve first
Before starting any task, read:
- `.brain/knowledge/projects/compound-brain.md`
- `.brain/memory/feedback_rules.md`

### 2. Capture after sessions
- Update `.brain/knowledge/daily/YYYY-MM-DD.md`
- Update `.brain/knowledge/projects/compound-brain.md` when state changes
- Add QMP entries for reusable patterns
- Log decisions in `.brain/knowledge/decisions/log.md`
- Update `.brain/knowledge/skills/skill-graph.md`

---

## Auto-Improvement Protocol

Every session should leave the brain more useful than before:
1. Update daily note
2. Update project state
3. Promote reusable patterns to QMP
4. Update skills if capabilities changed
5. Log strategic decisions
6. Update cron docs if scheduling changed
