# Community Contribution Lanes

`compound-brain` should grow through bounded community surfaces, not by letting
every contribution mutate the orchestration kernel directly.

## Core rule

Community contributions should usually land in one of these lanes first:

- `community/skills/`
- `community/departments/`
- `community/source-packs/`
- `community/evaluators/`
- `community/case-studies/`
- `community/benchmarks/`
- `community/promotions/`

The runtime core stays in:

- `scripts/`
- `policy-seed/`
- `templates/`
- `install.sh`
- core architecture files

## Why this structure exists

The repo needs two things at once:

- strong community input
- a stable orchestrator kernel

The community lanes let contributors bring new skills, evaluator ideas,
department operating models, and real-world evidence without weakening the
approval, trust, and runtime rules that make the system credible.

## How the loop should work

1. User activates `compound-brain` on a real repo.
2. User observes wins, failures, missing skills, or missing source packs.
3. User contributes a bounded artifact here.
4. Maintainers review for evidence, transferability, and safety.
5. Approved patterns are promoted into templates, seeds, or runtime defaults.

## What maintainers should ask for

- proof that the pattern helped
- scope: repo-specific or cross-project
- validator or evaluator path when relevant
- modern references or source quality
- failure modes and anti-goals

## What maintainers should reject

- broad autonomy changes without evidence
- prompt-only ideas with no validation path
- duplicate skills that do not add new capability
- unbounded external-source scraping
- changes that create a second Claude/Codex control plane

## Start here

- [Skills](./skills/README.md)
- [Departments](./departments/README.md)
- [Source Packs](./source-packs/README.md)
- [Evaluators](./evaluators/README.md)
- [Case Studies](./case-studies/README.md)
- [Benchmarks](./benchmarks/README.md)
- [Promotions](./promotions/README.md)
