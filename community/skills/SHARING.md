# Skill Sharing Guide

Skills in compound-brain live at four scopes. This document explains when to
use each and how to share skills across an org or team privately — without
publishing them to the community.

## The four scopes

```
┌─────────────────────────────────────────────────────────────┐
│  repo-local                                                 │
│  .claude/skills/  or  .brain/knowledge/skills/              │
│  Overrides everything. One repo only.                       │
├─────────────────────────────────────────────────────────────┤
│  personal global                                            │
│  ~/.claude/skills/                                          │
│  All your repos. Only on your machine.                      │
├─────────────────────────────────────────────────────────────┤
│  org / team  (private Git repo)                             │
│  Shared across your team's repos. Not public.               │
├─────────────────────────────────────────────────────────────┤
│  community                                                  │
│  community/skills/ in this repo                             │
│  Public. Peer-reviewed. Available to everyone.              │
└─────────────────────────────────────────────────────────────┘
```

Scopes are searched in this order. Repo-local always wins.

---

## When to use each scope

| Situation | Scope |
|-----------|-------|
| Skill is specific to one repo (custom tone, internal API patterns) | repo-local |
| Skill is only useful on your machine or personal workflow | personal global |
| Skill is valuable across your team's repos but contains internal IP or is not polished enough for public | org/team |
| Skill is general enough to help any project of that type | community |

If you are unsure: start at repo-local, promote to org when a second repo needs
it, promote to community when it has evidence and no internal IP.

---

## Setting up an org/team skill repo

### 1. Create a private repo

```bash
# GitHub
gh repo create your-org/org-skills --private

# Or any private Git host
git init org-skills && cd org-skills
```

### 2. Structure it like community/skills/

```
org-skills/
├── README.md
├── your-skill-name/
│   └── SKILL.md        ← same format as community/skills/TEMPLATE.md
└── another-skill/
    └── SKILL.md
```

Each `SKILL.md` must have `## Trigger Signals` for auto-detection to work.

### 3. Register it as a source

Add the repo to your team's `skill-discovery-sources` source pack override.
Create `.brain/knowledge/departments/engineering-sources.md` in any activated
repo, or add it directly to your personal source pack override:

```markdown
## Org Skill Sources (append to approved sources)

- `https://api.github.com/repos/your-org/org-skills/contents/`
  — Internal org skills. Requires GITHUB_TOKEN in env for private access.
```

Or add it to `.brain/state/skill-sources.json`:

```json
{
  "extra_sources": [
    {
      "name": "org-skills",
      "url": "https://api.github.com/repos/your-org/org-skills/contents/",
      "auth": "github_token",
      "scope": "org"
    }
  ]
}
```

### 4. Install on each team member's machine

```bash
# Clone to personal global skills
git clone git@github.com:your-org/org-skills.git ~/.claude/skills/org-skills

# Or symlink individual skills
ln -s ~/path/to/org-skills/your-skill ~/.claude/skills/your-skill
```

For Codex:
```bash
ln -s ~/path/to/org-skills/your-skill ~/.agents/skills/your-skill
```

For OpenCode:
```bash
ln -s ~/path/to/org-skills/your-skill ~/.config/opencode/skills/your-skill
```

### 5. Keep it fresh

Add a cron to pull updates:

```bash
# In crontab or CI
cd ~/.claude/skills/org-skills && git pull --ff-only
```

Or let compound-brain's cron handle it if the repo is registered in the
source pack — it will detect stale skills and propose refreshes via the
promotion inbox.

---

## Promoting a skill from org to community

When a skill has:
- no internal IP or proprietary patterns
- evidence it helped (before/after, case study)
- `## Trigger Signals`, `## Anti-goals`, and `## Evidence` sections filled out
- works for repos beyond your org

Submit it to `community/skills/` via a PR to this repo using
[TEMPLATE.md](./TEMPLATE.md). Maintainers review for scope, safety, and
duplicate overlap before merging.

---

## Skill sharing across repos within one org (without a separate skill repo)

If your team works in a monorepo or a small number of repos and does not want
a dedicated skill repo, the simplest option is:

1. Put shared skills in one repo's `.claude/skills/` (e.g., the main platform repo)
2. Symlink from other repos:

```bash
# From another repo
ln -s /path/to/platform-repo/.claude/skills/your-skill .claude/skills/your-skill
```

3. The skill-gap-detector finds it in `.claude/skills/` (repo-local scope) and
   treats it as active for that repo.

This works for small teams. For larger teams or frequent updates, a dedicated
private skill repo is cleaner.

---

## What NOT to put in community skills

- Internal API patterns, auth flows, or proprietary data models
- Skills that reference private URLs, internal hostnames, or env-specific config
- Skills that only make sense for your specific product domain
- Anything requiring a non-public credential to function

These belong in org/team scope or repo-local scope permanently.
