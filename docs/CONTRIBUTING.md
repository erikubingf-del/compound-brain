# Contributing

Contributions should reinforce the final lifecycle:

- global install once
- read-only preview for non-activated repos
- explicit `prepare-brain`
- explicit `activate-repo`
- self-hosting `compound-brain` with a fixed evaluator

## Contribution lanes

Default to the bounded community lanes first:

- `community/skills/`
- `community/departments/`
- `community/source-packs/`
- `community/evaluators/`
- `community/case-studies/`
- `community/benchmarks/`
- `community/promotions/`

These are the preferred places for community growth because they let the system
learn from real use without destabilizing the orchestration kernel.

Read:

- [`community/README.md`](../community/README.md)
- [`docs/community-maintainers.md`](./community-maintainers.md)

## High-value areas

- preview cache quality
- `prepare-brain` scaffolding
- activation approvals
- department runtime and bounded loops
- fixed-evaluator autoresearch
- promotion inbox review
- self-hosting evaluator and scorecard automation
- Claude/Codex parity through one repo control plane

## What makes a strong contribution

- It solves one clear problem.
- It includes evidence, not just enthusiasm.
- It fits a repo type, department, or evaluator lane cleanly.
- It respects one shared Claude/Codex control plane.
- It explains failure modes and anti-goals.

## Guardrails

- Do not introduce a second repo runtime for Codex.
- Do not let project code write directly into global PARA/QMP/skills.
- Do not weaken approval gates for strategic changes.
- Do not let self-improvement loops rewrite the evaluator automatically.

## Core-runtime changes

Changes to the runtime kernel should be rarer and more evidence-heavy than
community lane contributions.

If a change touches:

- `scripts/`
- `policy-seed/`
- `templates/`
- `install.sh`
- trust/depth/approval/runtime contracts

then it should include:

- a clear reason the change must touch core
- evidence from real repo use, case studies, or benchmarks
- explicit migration and risk notes
- tests or dry-run verification where relevant

## Basic checks

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
bash install.sh --dry-run
```
