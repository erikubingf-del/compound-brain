# Operator Note: promptCacheTtl for Scheduled Routines

**Source:** Official docs w35 — https://code.claude.com/docs/en/prompt-caching#choose-the-ttl-yourself
**Added:** 2026-09-21

## What

Setting `promptCacheTtl: "1h"` in user settings keeps a one-hour prompt cache on the main conversation when using an API key or cloud provider. `subagentPromptCacheTtl` sets the TTL for subagents and all requests outside the main conversation.

## Why this matters for brain routines

Weekly digest and other scheduled routines fire into a fresh session with a cold context. At 1M-token context budgets (Sonnet 5, Fable 5.1), a cache miss on the full CLAUDE.md + brain state read is expensive. If the routine re-fires within the hour (retry on failure, manual re-run), the second run pays only for uncached tokens.

## To apply

Add to user settings (`~/.claude/settings.json`):
```json
"promptCacheTtl": "1h",
"subagentPromptCacheTtl": "5m"
```

**Needs approval** — modifying user settings is outside the SAFE allowlist.
