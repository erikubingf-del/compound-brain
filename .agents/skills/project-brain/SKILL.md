---
name: project-brain
description: Use for substantial coding or project work, cross-session handovers, decisions, research, new project onboarding, or a correction to an existing plan. Recover the approved goal and latest authoritative evidence, preserve decisions, verify actions, and turn material errors into regression tests.
---

# Project Brain — portable Codex workflow

This skill is a **process**, not a source of project facts or a substitute for permissions.
Use the smallest relevant context and avoid re-reading unrelated personal records.

## 1. Recover the mission before making a consequential change

1. Read the nearest repository `AGENTS.md` and `CLAUDE.md`, if present.
2. Check `.brain/memory/project_context.md`, `.brain/memory/feedback_rules.md`,
   current project decisions, approved plans, tests and source versions when available.
3. In **local Codex**, read `~/.codex/global-agent-governance.md` if it exists.
   This may contain a private Global Agent Operations Board link. A URL alone is
   **not evidence that the private Page was read**.
4. In **Codex Cloud**, use an explicitly connected authorized tool or MCP server
   to retrieve private project Pages only if it is actually available. Never
   assume that ChatGPT Memory, custom instructions, or private Pages are shared
   with Codex. If unavailable, use the repository's verified sources and state
   the material limitation.
5. Identify the **approved objective, measurable success criterion, deadline,
   constraints, owner and next decision**. Treat older memory as context, not proof.

## 2. Source hierarchy and decision quality

- Current primary record or verified live source > dated accepted decisions >
  historical project notes > model memory > assumptions.
- Label consequential inputs **CONFIRMED / ESTIMATE / PROPOSAL / UNKNOWN**.
  Flag conflicts, missing sources and stale dates instead of silently reconciling.
- Compare new options with the user's original priorities, existing purchases,
  commitments, compatibility, total cost and downstream effects.
- Work backward from the agreed target into milestones and measurable evidence.
  Do not replace an approved goal merely because an alternative is mentioned.
- Preserve distinct people, projects and confidential data boundaries.

## 3. Execute with approvals and receipts

1. Make a concise plan grounded in current source files and known constraints.
2. Change only authorized files and surfaces. Respect repo approval, trust and
   autonomy-depth gates; do not send, trade, purchase, delete or change account
   settings without the required approval.
3. Verify with relevant tests, diffs and actual tool receipts.
4. Never call a proposed or unverified action "done".
5. When a plan changes, explain the exact delta, evidence and consequences.
   Preserve the old baseline for later comparison.

## 4. Handover, new themes and lessons

For substantial work, leave a short handover in the **existing** canonical
project record, not a duplicate "master" file:
- Objective and deadline; current verified state and source versions.
- Accepted decisions versus proposals; open blockers and next authorized step.
- Actual tests/receipts and their results.

For a new theme, identify the existing project hub before creating another.
If a connected Global Board is writable and authorized, register the project
once; otherwise leave a **PENDING ONBOARDING** note locally and report the
missing connection. Do not claim a global board update without a verified write.

For a material failure or repeated user correction, record:
**incident -> root cause -> correction -> regression test -> evidence -> status**.
Keep incidents open until a later real run passes the test; an updated prompt
alone is not proof of correction.

## 5. Cross-environment honesty

- Repository-local `.agents/skills/project-brain/SKILL.md` is available to
  Codex when this repository or a prepared project is checked out and its skills
  are discovered. User-global `~/.agents/skills/project-brain` requires a local
  installation and does not automatically appear in Codex Cloud.
- A private ChatGPT Page is authoritative only when retrieved through an
  authorized connection. A local pointer or public governance summary is a
  fallback, **not live synchronization**.
- Do not commit private Board URLs, credentials, medical details, personal
  financial information or private project files into public repositories.

<!-- compound-brain managed portable skill -->
