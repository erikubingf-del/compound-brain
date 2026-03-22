# Source Pack Submission

## Name

`skill-discovery-sources` — External Skill Discovery Pack

## Department

engineering (all repos, all stacks)

## Objective

Provide the `skill-gap-detector` evaluator with a bounded list of approved
external sources where new skills can be discovered. On cron, the runtime
fetches the skill index from each source, scores new skills against the
current project's signals, and proposes good matches via the promotion inbox.

This pack is not for one skill or one repo type. It is the shared discovery
layer for the entire skill system — the mechanism by which new community skills
reach activated repos without human manual searching.

## Approved Sources

### Skill registries (GitHub repos publishing SKILL.md files)

- `https://api.github.com/repos/obra/superpowers/contents/skills`
  — Superpowers skill collection (debugging, TDD, code review, git worktrees,
  subagent-driven development, planning, verification)

- `https://api.github.com/repos/erikubingf-del/compound-brain/contents/community/skills`
  — compound-brain community skills (this repo — discovers peer contributions)

### Stack-specific reference sources

These are fetched when a specific stack signal is detected, not unconditionally:

| Signal | Source |
|--------|--------|
| `dep:react` or `dep:next` or `ext:tsx` | `https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md` |
| `dep:tailwindcss` | `https://tailwindcss.com/docs/responsive-design` |
| `dep:@shadcn/ui` | `https://ui.shadcn.com/docs` |
| `lang:python` or `dep:torch` or `dep:pandas` | `https://raw.githubusercontent.com/microsoft/ML-For-Beginners/main/README.md` |
| `lang:go` | `https://raw.githubusercontent.com/golang/go/master/doc/effective_go.md` |
| `lang:rust` | `https://doc.rust-lang.org/book/title-page.html` |
| `dep:prisma` or `dep:drizzle-orm` | `https://www.prisma.io/docs/guides/database/production-safeguards` |
| `dep:stripe` | `https://stripe.com/docs/development/quickstart` |

### GitHub search (cron only, monthly)

Search GitHub for new SKILL.md contributions matching the project's top signal:

```
https://api.github.com/search/code?q=filename:SKILL.md+in:path+.claude/skills
```

Filter results: only repos with > 10 stars, last pushed < 6 months ago.
Fetch the SKILL.md, score against project signals, propose if score > 2.

## Search Queries

When scanning GitHub skill registries, score each discovered SKILL.md by:
1. Extracting its `## Trigger Signals` section
2. Matching against current project signals (file extensions, deps, languages)
3. Only proposing skills with score ≥ 2 matched signals

## Recency Policy

- Skill registry indexes (GitHub API): check weekly
- Stack-specific reference docs: check monthly, or when dep version changes
- GitHub search: monthly only (rate limit awareness)
- Cache results in `.brain/state/source-pack-cache.json`

## Validation Policy

- Never apply a discovered skill automatically — always go through promotion inbox
- Human must review and approve before any skill enters `active[]`
- Reject skills with no `## Trigger Signals` section (unscoped skills are unsafe)
- Reject skills with no `## Anti-goals` section (unconstrained skills are unsafe)
- Reject skills that overlap > 80% with an already-active skill (duplicate)

## Disallowed Sources

- Unverified GitHub repos with < 10 stars or last pushed > 1 year ago
- AI-generated skill files with no evidence section
- Sources behind authentication walls
- Any URL not in this list — add here first before using

## Anti-goals

- Not a web scraper or broad GitHub trawl
- Not for fetching implementation libraries or code — skills only
- Not for replacing human judgment on which skills to activate
- Not for runtime code execution from external sources

## Why This Pack Helps

Without this pack, the skill system only grows when a human manually adds
skills. With it, the cron surfaces relevant skills from approved sources
automatically — a Python project gets ML skills proposed, a frontend project
gets UI skills proposed, a database-heavy project gets migration safety skills
proposed. The human still approves, but the discovery is automatic.
