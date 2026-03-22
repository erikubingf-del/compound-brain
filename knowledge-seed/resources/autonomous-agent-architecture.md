# Autonomous Agent Architecture

## Purpose
Use one shared control plane, explicit approvals, bounded execution lanes, and
durable memory so agent work compounds instead of drifting between sessions.

## Core Rules
- one repo brain per activated project
- one global brain for cross-project learning
- fixed evaluators before unattended experimentation
- review before global promotion
- logs and decisions must outlive the session that created them

## Applied to compound-brain
- `observe -> preview -> prepare -> activate`
- global promotion inbox
- department contracts plus approval-gated autonomy
