# Skill Contributions

Use this lane for reusable skills that help activated repos or the global
orchestrator.

Good fit:

- debugging skills
- UI/frontend skills
- deploy and operations skills
- finance or regulated-domain skills
- repo-specific patterns that may later become transferable

Each submission should include:

- the capability gap it solves
- the repo types or departments it fits
- trigger signals
- process steps
- validation or evaluator path
- failure modes
- examples of when it should not be used

Use [TEMPLATE.md](./TEMPLATE.md) as the contribution shape.

## Available Skills

| Skill | Best Fit | Trigger | Runtime |
|-------|----------|---------|---------|
| [ui-master](./ui-master/SKILL.md) | Next.js, React, SaaS frontend, dashboard, CRM | `.tsx`/`.jsx` present, UI/design request | [RUNTIME.md](./ui-master/RUNTIME.md) — session-start audit + cron source refresh |

Skills with a `RUNTIME.md` have full runtime integration: the session-start hook
auto-detects when the skill is needed, and the cron keeps it fresh by auditing
approved source packs. Skills without a `RUNTIME.md` are passive — loaded only
when explicitly invoked.
