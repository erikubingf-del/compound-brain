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

| Skill | Best Fit | Trigger Signals |
|-------|----------|----------------|
| [ui-master](./ui-master/SKILL.md) | Next.js, React, SaaS frontend, dashboard, CRM | `ext:tsx`, `ext:jsx`, `dep:react`, `dep:next`, `dep:tailwindcss` |

## How skills are auto-discovered

Skills are not installed manually per project. The `skill-gap-detector`
evaluator reads each skill's `## Trigger Signals` and scores them against
the project's actual file extensions, dependencies, and languages — on every
session start and cron run.

See [RUNTIME.md](./RUNTIME.md) for the full generic loop.

The key requirement for any skill to be auto-detectable: **it must have a
`## Trigger Signals` section with specific, observable signals** (file
extensions, dep names, language markers). Vague signals are ignored.
