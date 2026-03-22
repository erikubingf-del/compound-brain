# Community Maintainer Workflow

Use this workflow to keep community energy high without destabilizing the core.

## Review order

1. `community/case-studies/`
2. `community/benchmarks/`
3. `community/skills/`
4. `community/departments/`
5. `community/source-packs/`
6. `community/evaluators/`
7. `community/promotions/`
8. direct core-runtime changes

## Promotion criteria

A contribution should usually be promoted only if it is:

- evidence-backed
- transferable beyond one narrow repo
- safe under the current approval and depth model
- compatible with one Claude/Codex control plane
- understandable by maintainers and future contributors

## Default review outcomes

- `accept-as-community`
- `request-evidence`
- `request-scope-reduction`
- `promote-to-template`
- `promote-to-knowledge-seed`
- `promote-to-runtime`
- `reject`

## Maintainer questions

- What exact problem does this solve?
- What repo type or department does it fit?
- What proof suggests it improves outcomes?
- What validator or evaluator keeps it honest?
- What would break if this were widely adopted?
- Does it belong in the repo brain, the global brain, or nowhere yet?

## Strong rule

Do not merge broad runtime-behavior changes on enthusiasm alone.
Require evidence, bounded scope, and a clean migration path.
