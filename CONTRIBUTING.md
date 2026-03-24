# Contributing to compound-brain

Contributions should reinforce the final lifecycle:

- global install once
- read-only preview for non-activated repos
- explicit `prepare-brain`
- explicit `activate-repo`
- self-hosting `compound-brain` with a fixed evaluator

---

## Start here — community lanes

Default to the bounded community lanes first:

| Lane | What belongs here |
|------|-------------------|
| `community/skills/` | Skills for specific repo types or stacks |
| `community/departments/` | Department operating models |
| `community/source-packs/` | Approved external research sources |
| `community/evaluators/` | Fixed evaluators for bounded autonomy |
| `community/case-studies/` | Real activated-repo outcomes |
| `community/benchmarks/` | Evidence that changes actually help |
| `community/promotions/` | Cross-project pattern candidates |

These are the preferred places for community growth because they let the system
learn from real use without destabilizing the orchestration kernel.

See [`community/README.md`](community/README.md) for lane-specific rules.

---

## What makes a strong contribution

- It solves one clear problem in a real activated repo.
- It includes evidence, not just enthusiasm — logs, scorecard output, or benchmark data.
- It fits a repo type, department, or evaluator lane cleanly.
- It respects one shared Claude/Codex control plane — no parallel runtimes.
- It explains failure modes and anti-goals explicitly.

---

## High-value areas

- preview cache quality — better goal and department inference
- `prepare-brain` scaffolding — more accurate initial context
- activation approvals — smoother goal confirmation UX
- department runtime and bounded loops — richer mission packets
- fixed-evaluator autoresearch — more evaluator examples
- promotion inbox review — better cross-project pattern extraction
- self-hosting evaluator and scorecard automation — compound-brain self-improvement
- Claude/Codex parity — closing the hook parity gap

---

## Guardrails

- Do not introduce a second repo runtime for Codex.
- Do not let project code write directly into global PARA/QMP/skills.
- Do not weaken approval gates for strategic changes.
- Do not let self-improvement loops rewrite the evaluator automatically.

---

## Core-runtime changes

Changes to the runtime kernel should be rarer and more evidence-heavy than
community lane contributions.

If a change touches `scripts/`, `policy-seed/`, `templates/`, `install.sh`,
or trust/depth/approval/runtime contracts, it should include:

- a clear reason the change must touch core
- evidence from real repo use, case studies, or benchmarks
- explicit migration and risk notes
- tests or dry-run verification

---

## Checks before submitting

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
bash install.sh --dry-run
```

---

See [`docs/community-maintainers.md`](docs/community-maintainers.md) for maintainer
responsibilities and promotion review process.
