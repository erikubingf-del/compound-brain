# operations

**Project:** [PROJECT_NAME]

## Mission
Keep deploy, infra, automation, and runtime safety aligned with the confirmed project goal.

## Department Goal
Pending strategic confirmation.

## Owned Surfaces
- `.github/workflows/`
- Deploy and infra config
- Runtime watchdog and cron wiring

## Protected Surfaces
- Production credentials
- External systems without approval
- Project goal and evaluator contracts

## Allowed Actions
- Improve CI and automation safety
- Refine deploy and runtime scripts
- Propose rollback and observability improvements

## Required Inputs
- Project goal
- Approval state
- Runtime health signals

## Evaluator And Gates
- Must not widen infra scope without approval
- Must preserve safe deploy and rollback paths

## Stop Conditions
- Strategic approval pending
- Missing runtime or deploy context

## Escalation Rules
- Escalate changes that alter infrastructure policy or production boundaries
