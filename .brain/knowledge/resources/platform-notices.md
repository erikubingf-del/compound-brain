# Platform Notices — Breaking Changes & Standing Alerts

Append-only. Add entries at the top; each entry carries a date and version range.
brain-orient reads this file. Plugin SKILL.md embeds the current standing alerts
so they surface in every project — update the plugin when a new alert lands here
(NEEDS APPROVAL to touch plugins/).

---

## 2026-09-21 — Breaking: Task tools absent on Sonnet 5 / Fable 5+ (v2.1.233+)

**Affected:** any skill, routine, or prompt that calls `TaskCreate`, `TaskUpdate`,
`TodoWrite`, or `TodoRead`.

`TaskCreate`/`TaskUpdate`/`TodoWrite` (and related) are no longer available on
Sonnet 5, Fable 5, Mythos 5, and later model families. **Failure is silent** —
calls do nothing, return no error, and the workflow appears to succeed.

**Fix:** set `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` in the session environment, or
migrate to queue.md-style state (already the pattern in this brain).

**Audit:** `.brain/routines/`, `plugins/compound-brain/skills/`, any project
SKILL.md or hook that referenced these tools.

[VERIFIED: https://code.claude.com/docs/en/tools-reference#task-tool-availability]

---

## 2026-09-21 — Breaking: `defaultMode: bypassPermissions` blocked in project settings (v2.1.251+)

**Affected:** any project `.claude/settings.json` or `.claude/settings.local.json`
that set `"defaultMode": "bypassPermissions"`.

This setting **no longer takes effect** in project-level files; the session silently
falls back to Manual mode. Move it to user or managed settings, or pass
`--permission-mode bypassPermissions` on the CLI.

[VERIFIED: https://code.claude.com/docs/en/permission-modes#which-mode-a-session-starts-in]

---

## 2026-09-21 — New: `promptCacheTtl` reduces scheduled-routine cold-start cost

Set `"promptCacheTtl": "1h"` in user settings for a one-hour prompt cache on the
main conversation (API key / cloud provider sessions). Especially useful for
weekly digest and other cron sessions that fire into a cold context.
`subagentPromptCacheTtl` sets the TTL for subagents.

Needs approval to set in user settings. Full note: `resources/prompt-cache-ttl-note.md`.

[VERIFIED: https://code.claude.com/docs/en/prompt-caching#choose-the-ttl-yourself]

---

## 2026-09-21 — New: `claude plugin eval` makes skill routing testable (v2.1.269+)

`claude plugin eval` runs a plugin against test cases, compares against a no-plugin
baseline, and scores with graders. The `tool_used: Skill` grader specifically checks
whether a prompt routes to the intended skill — the most common silent failure mode
in multi-skill plugins.

Run `claude plugin eval init` from `plugins/compound-brain/` to draft a baseline suite.
Needs approval: `init` writes eval files.

[VERIFIED: https://code.claude.com/docs/en/plugin-evals]

---

## Standing: This repo is PUBLIC — no project/service/host names in .brain/

Git history is permanent. All specific names belong in the private stored prompt, never
here. Generic risk categories only.

[Established: 2026-08-04]
