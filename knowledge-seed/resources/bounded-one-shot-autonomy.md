# Bounded One-Shot Autonomy

## Goal
Finish concrete work in one pass when scope, validation, and rollback boundaries
are clear.

## Required Pattern
- build a task packet first
- preload only the relevant context
- keep the execution lane isolated
- run deterministic checks before broad validation
- cap repair loops
- finish with logs and memory capture

## Why it matters here
compound-brain should automate aggressively only when the evaluator and scope
are explicit enough to keep the system trustworthy.
