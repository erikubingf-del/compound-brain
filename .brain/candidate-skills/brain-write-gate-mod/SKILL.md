# Candidate Skill: brain-write-gate-mod

**Status:** draft — NEEDS APPROVAL to promote to `plugins/` or `.claude/skills/`
**Source:** 2026-10-05 digest, SAFE-2 auto-apply item
**Type:** Claude Code Mod (plugin middleware, not a skill/slash command)

---

## Purpose

Enforce the SAFE write boundary for unattended (cron/cloud) sessions:
any Write, Edit, or Bash call that would create or modify a file outside
`.brain/**` is intercepted and blocked before execution.

This is the deterministic enforcement layer that CLAUDE.md instructions
alone cannot provide — a session that can rewrite its own instructions
can bypass prose rules; a Mod hook fires at the tool boundary and has no
instruction surface to rewrite.

---

## Architecture

Claude Code Mods (released Oct 2026, requires v2.1.287+) run as plugins
with access to PreToolUse hooks. A Mod can:

- Inspect the tool call (tool name + parameters) before execution
- Return `block` to prevent execution with a reason message
- Return `approve` to allow
- Return `rewrite` to modify the call before it reaches the tool

This Mod uses `block` for any write outside `.brain/**`.

---

## Proposed Hook Logic (pseudocode)

```javascript
// mod.js — PreToolUse hook
export default function preToolUse({ toolName, toolInput }) {
  const writeTools = ['Write', 'Edit', 'Bash'];
  if (!writeTools.includes(toolName)) return { action: 'approve' };

  // For Bash, check if the command writes outside .brain/
  if (toolName === 'Bash') {
    const cmd = toolInput.command ?? '';
    // Only block if the command clearly writes outside .brain
    // Conservative: if command contains a path outside .brain/ and
    // is a write operation (>, tee, cp, mv to, sed -i, rm outside .brain)
    if (/\b(>|>>|tee|cp|mv|sed\s+-i|rm)\b/.test(cmd) &&
        !cmd.includes('.brain/')) {
      return {
        action: 'block',
        reason: 'brain-write-gate: unattended write outside .brain/ blocked'
      };
    }
  }

  // For Write/Edit, check file_path parameter
  const path = toolInput.file_path ?? toolInput.path ?? '';
  if (path && !path.includes('.brain/')) {
    return {
      action: 'block',
      reason: `brain-write-gate: write to ${path} blocked — unattended sessions may only write under .brain/`
    };
  }

  return { action: 'approve' };
}
```

---

## Activation Requirements

1. Claude Code v2.1.287+
2. Create `plugins/brain-write-gate/` with `plugin.json` and `mod.js`
3. `/plugin install` from the repo root (or add to `.claude/plugins/`)
4. Human-attended first run to verify the gate fires as expected
5. NEEDS APPROVAL before any of steps 2–4

---

## Risks and Limits

- The Bash path check is heuristic — a sufficiently complex command could evade it.
  Definitive protection requires an allowlist-only Bash policy (queue 011).
- A mod that blocks git operations would break the commit/push step.
  Exempt: `git add .brain/`, `git commit`, `git push` commands.
- Does not protect against MCP tool writes (e.g., filesystem MCP). Separate gate needed.
- First run attended so the human can approve git operations that the gate would otherwise
  flag.

---

## Promotion Path

1. Human reviews this spec
2. Implements `plugins/brain-write-gate/` (NEEDS APPROVAL — touches `plugins/`)
3. Run `claude plugin eval init` to generate test suite
4. Pass eval before enabling in unattended sessions
