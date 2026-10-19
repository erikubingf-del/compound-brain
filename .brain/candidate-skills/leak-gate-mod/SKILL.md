# Candidate: Leak-Gate Mod

**Type:** Mod (plugin hook), NOT a skill  
**Status:** Candidate — drafting is SAFE; promotion to `.claude-plugin/` requires human review  
**Priority:** High — repo is currently public; this is defense-in-depth until visibility changes (queue-007)

---

## What It Does

A Claude Code mod that intercepts Write, Edit, and push actions and blocks or redacts
project/host/strategy names before they reach disk or git history.

The specific name patterns live in the private stored prompt only — they must NOT appear
in this file or any tracked file (this repo is public; git history is permanent).

---

## Why a Mod, Not a Skill

- A **skill** loads instructions into context: Claude reads them and tries to comply.
  Skills can be forgotten, skipped by context pressure, or overridden by a later instruction.
- A **mod** registers hooks that run deterministically in Claude's control plane.
  A `tool.check` hook fires on every Write/Edit/Bash tool call before it executes.
  A `prompt.change` hook fires before the prompt reaches the model.

For leak prevention, deterministic enforcement is required. Instructions alone are not enough.

---

## Hook Architecture

### Hook 1: `tool.check` on Write/Edit/Bash

Fires before any file write or shell command. Scans the outgoing content for name patterns.

```
if content matches any leak pattern:
  return { block: true, reason: "leak-gate: name pattern detected — remove before continuing" }
```

This is the primary gate. It fails closed: if the hook crashes, `onFailure: "block"` ensures
the write does not proceed.

### Hook 2: `prompt.change` (optional secondary)

Fires before the prompt is sent to the model. Can redact detected patterns from the
outgoing prompt so the model never sees them in a context that could reflect them back.

This is a secondary defense for cases where names appear in user input before reaching
the tool-call stage.

---

## Config Shape (conceptual — actual plugin.json written at promotion time)

```json
{
  "hooks": [
    {
      "event": "tool.check",
      "tools": ["Write", "Edit", "Bash"],
      "handler": "hooks/leak-gate.js",
      "onFailure": "block"
    },
    {
      "event": "prompt.change",
      "handler": "hooks/leak-gate-prompt.js",
      "onFailure": "allow"
    }
  ]
}
```

`onFailure: "block"` on the tool-check hook: if the hook crashes or times out, the
write is blocked (fail-closed). The prompt hook uses `allow` because blocking a prompt
on hook error would make the session unusable.

---

## Promotion Path

1. Human reviews this candidate and agrees it's the right approach.
2. A PR is opened to add `plugins/compound-brain/hooks/leak-gate.js` with the actual
   pattern list (sourced from the private stored prompt, never hardcoded here).
3. The PR is reviewed for correctness and the pattern list is verified complete.
4. After merge, the plugin is enabled in a test session before enabling in cron.

**Do not promote from an unattended session.** Content written to `.claude-plugin/` or
`plugins/` executes as instructions in every session where the plugin is enabled.
This candidate must be reviewed by a human before promotion.

---

## Related Queue Items

- Queue-007: repo visibility (public → private) — the primary fix; this mod is defense-in-depth
- Queue-011: Bash allowlist narrowness — related trust boundary
