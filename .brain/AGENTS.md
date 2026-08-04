# Brain Agent Learnings

Append-only log of cross-run insights from scheduled routines.
Each entry: date | routine | learning. Never edit prior entries.

---

## 2026-08-03 | weekly-digest | Bootstrap

- **Ralph Loop adopted for all routines**: fresh context each run, state in this repo, learnings here. Each routine reads this file first, appends at end. No carry-over except what's on disk.
- **3 of 4 native-feature claims from third-party blogs failed verification against official docs.** Rule: verify against code.claude.com official docs or tag [UNVERIFIED] — never implement unverified native feature claims.
- **Next priorities**: CLAUDE.md hierarchical audit (queue 002), SAGE write-gate prototype before any vector memory (queue 005).

---

## 2026-08-04 | weekly-digest | Run 2

- **/doctor (v2.1.205+) solves queue-002 natively**: it audits CLAUDE.md for derivable content, deduplicates local vs checked-in copies, and proposes trims with confirmation. Run /doctor FIRST before any manual CLAUDE.md audit — it reduces manual work to reviewing its proposals.
- **Hook matchers changed in w27**: hyphenated identifiers now exact-match, not substring-match. If any hook in .claude/hooks/ uses a hyphenated name to catch all tools from an MCP server, update it to `mcp__server-name__.*` pattern before it silently breaks.
- **"Always allow" permissions now persist across sessions and worktrees** (save at repo root). One deliberate setup session approving routine tools eliminates all cron prompt friction — worth doing as a dedicated step before next autonomous run.
