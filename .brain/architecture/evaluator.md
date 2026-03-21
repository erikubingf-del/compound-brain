# Evaluator

## Protected Invariants
- Single repo control plane
- Global and repo memory separation
- Approval-gated strategic changes
- Fixed evaluator cannot self-rewrite without approval

## Deterministic Gates
- Unit tests must pass
- Installer dry-run must pass
- Activation smoke test must pass
- Self-hosting runtime schema must remain intact

## Architecture Rubric
- Control-plane integrity
- Claude/Codex parity
- Approval safety
- Upgradeability
- Autonomy boundedness
- Observability and log quality

## Keep Thresholds
- deterministic_gates: required
- architecture_rubric: no regression
- canary_behavior: neutral_or_better

