# Contributing

Contributions should reinforce the final lifecycle:

- global install once
- read-only preview for non-activated repos
- explicit `prepare-brain`
- explicit `activate-repo`
- self-hosting `compound-brain` with a fixed evaluator

## High-value areas

- preview cache quality
- `prepare-brain` scaffolding
- activation approvals
- department runtime and bounded loops
- fixed-evaluator autoresearch
- promotion inbox review
- self-hosting evaluator and scorecard automation
- Claude/Codex parity through one repo control plane

## Guardrails

- Do not introduce a second repo runtime for Codex.
- Do not let project code write directly into global PARA/QMP/skills.
- Do not weaken approval gates for strategic changes.
- Do not let self-improvement loops rewrite the evaluator automatically.

## Basic checks

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
bash install.sh --dry-run
```
