---
title: compound-brain Deployment
area: deployment
updated: 2026-03-21
---

# compound-brain — Deployment

## Stack
_(document deployment stack)_

## Deploy Steps
_(document steps)_

## Critical Rules (P1)
- Always commit and push before issuing deploy commands
- Never use `prisma db push --accept-data-loss` in production
- Always use `prisma migrate deploy` for production migrations

## Environment Variables
_(document .env structure)_

## Known Issues / Gotchas
_(add as discovered)_
