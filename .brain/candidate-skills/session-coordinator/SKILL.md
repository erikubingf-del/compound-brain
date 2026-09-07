# Candidate Skill: session-coordinator

**Status:** draft — awaiting human review and promotion
**Source:** 2026-09-07 digest, w32/w34 cross-session messaging findings
**Risk to promote:** NEEDS APPROVAL — writes to `plugins/compound-brain/skills/`

---

## Purpose

Coordinate task dispatch and completion between multiple Claude Code sessions on
the same machine or cloud environment using the `ListAgents` / `SendMessage` /
`notify_when_idle` primitives (available v2.1.224+).

Enables: parallel research lanes, fan-out + collect workflows, and idle-gated
handoffs without polling or external broker processes.

---

## When to invoke

Invoke this skill when the current task has 2+ independent subtasks that could
run concurrently and you need each result before synthesizing.

Typical use: weekly digest with 4 independent search lanes.

---

## Pattern

```
1. ListAgents — discover live sessions reachable from this session
2. For each available worker session:
     SendMessage(to: session, message: "<task instruction>")
     SendMessage(to: session, message: "<task instruction>", notify_when_idle: true)
3. Wait for notify_when_idle signals
4. Read each worker's output from a shared agreed-upon file path under .brain/tmp/
5. Synthesize and write final output
```

### Safety constraints

- Messages are text only; no file sharing over the message channel
- Loop throttle is enforced by Claude Code — repeated messages from same sender
  are rate-limited automatically
- Workers must write output to agreed `.brain/tmp/<task-id>.md` paths, not to
  persistent memory directly; orchestrator reviews before promoting
- Never spawn more concurrent sessions than the `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`
  limit (default: 20 per session)

---

## Inputs

- `task_description` (string): the instruction to send to each worker
- `worker_count` (int, default 1): how many sessions to dispatch to
- `output_path_prefix` (string): `.brain/tmp/<prefix>-<n>.md` where each worker writes results

---

## Output

- A synthesized summary written to the caller's conversation
- Raw worker outputs retained at `output_path_prefix` paths for review

---

## Known limitations

- Only works on macOS, Linux, and Windows (v2.1.234+ for Windows)
- Session names are non-deterministic; `ListAgents` must be called at runtime
- Workers must already be running; this skill does not start new sessions
- `notify_when_idle` delivers one notice per invocation; multi-step workers need
  to send their own signal at completion

---

## Promotion checklist (human review)

- [ ] Verify no sensitive session data leaks through message text
- [ ] Confirm `.brain/tmp/` path is gitignored (check .gitignore)
- [ ] Test with 2 live sessions before enabling in production routines
- [ ] Add to compound-brain plugin manifest after promotion
