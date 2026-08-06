# Proposal 003 — Close the self-modification hole in `.claude/settings.json`

Status: **proposal only — needs owner action.** Settings edits are denied to
sessions by `.claude/settings.json` itself, so this cannot be self-applied.
That is the gate working correctly; it is also why it is sitting here.

## The finding

`.claude/settings.json` currently lists in `permissions.allow`:

```json
"Write(.claude/skills/**)",
"Edit(.claude/skills/**)",
```

Those two lines were added mid-session on 2026-08-04 so that skills could be
authored, and they were never narrowed afterward. Their effect is that the
**unattended weekly run can rewrite its own instructions** — including
`.claude/skills/brain-digest/SKILL.md`, which contains the definition of what
counts as a SAFE self-applied change. A constraint a process can edit is not a
constraint on that process.

The routine's inputs are pages on the open web. The distance between "SAFE
markdown" and "instructions that run in future sessions" is the whole security
model, and right now that distance is zero for `.claude/skills/`.

## The change

1. **Delete** the two `Write/Edit(.claude/skills/**)` entries from `allow`.
2. **Add** them to `deny` instead. The project skills are superseded by the
   plugin at `plugins/compound-brain/skills/`; freezing them is correct.
3. **Add an `ask` tier** for the published surfaces. `ask` is the right verb
   rather than `deny`: an attended session can approve a promotion, while an
   unattended run has nobody to answer the prompt and therefore fails closed.
4. **Harden the `CLAUDE.md` rules** with path variants. Bare `Write(CLAUDE.md)`
   may not match `./CLAUDE.md` or an absolute path; for a file this
   load-bearing, matching semantics should not be assumed. Verify against
   <https://code.claude.com/docs/en/permissions>.

## Apply this

Replace the `permissions` object with:

```json
"permissions": {
  "allow": [
    "Read", "Glob", "Grep", "WebSearch", "WebFetch",
    "Write(.brain/**)", "Edit(.brain/**)",
    "Bash(git status*)", "Bash(git status:*)",
    "Bash(git diff*)", "Bash(git diff:*)",
    "Bash(git add*)", "Bash(git add:*)",
    "Bash(git commit*)", "Bash(git commit:*)",
    "Bash(git push*)", "Bash(git push:*)",
    "Bash(git fetch*)", "Bash(git fetch:*)",
    "Bash(git log*)", "Bash(git log:*)",
    "Bash(git grep*)", "Bash(git grep:*)",
    "Bash(git ls-files*)", "Bash(git ls-files:*)",
    "Bash(git rev-parse*)", "Bash(git rev-parse:*)",
    "Bash(git branch*)", "Bash(git branch:*)",
    "Bash(ls*)", "Bash(ls:*)",
    "Bash(mkdir -p .brain*)", "Bash(mkdir -p .brain:*)"
  ],
  "ask": [
    "Write(plugins/**)", "Edit(plugins/**)",
    "Write(.claude-plugin/**)", "Edit(.claude-plugin/**)",
    "Write(install.sh)", "Edit(install.sh)"
  ],
  "deny": [
    "Bash(git push --force*)", "Bash(git push -f*)",
    "Bash(git reset --hard*)", "Bash(git clean*)", "Bash(rm -rf*)",
    "Write(.claude/skills/**)", "Edit(.claude/skills/**)",
    "Write(CLAUDE.md)", "Edit(CLAUDE.md)",
    "Write(./CLAUDE.md)", "Edit(./CLAUDE.md)",
    "Write(**/CLAUDE.md)", "Edit(**/CLAUDE.md)",
    "Write(core/BRAIN.md)", "Edit(core/BRAIN.md)",
    "Write(**/core/BRAIN.md)", "Edit(**/core/BRAIN.md)",
    "Write(.claude/settings.json)", "Edit(.claude/settings.json)",
    "Write(.claude/settings.local.json)", "Edit(.claude/settings.local.json)",
    "Write(.claude/hooks/**)", "Edit(.claude/hooks/**)",
    "Write(.mcp.json)", "Edit(.mcp.json)",
    "Write(scripts/**)", "Edit(scripts/**)",
    "Write(.gitignore)", "Edit(.gitignore)"
  ]
}
```

## Resulting trust boundary

An unattended run may write things that **describe** the world. It may not
write things that **execute** in other repos, and it may not write the rules
that constrain itself.

| Surface | Unattended run |
|---|---|
| `.brain/**` (digests, learnings, queue, candidate-skill drafts) | allowed — blast radius is one repo, reviewable as a diff, inert until promoted |
| `plugins/**`, `.claude-plugin/**`, `install.sh` | **ask** — attended promotion only; fails closed unattended |
| `.claude/skills/**` | **denied** — superseded by the plugin, and self-instruction editing |
| `CLAUDE.md`, `core/BRAIN.md`, settings, hooks, MCP, scripts, `.gitignore` | denied |

## Sequencing note

Do **not** delete `.claude/skills/` until the plugin has been confirmed to load
in a real routine/cloud session. `.brain/AGENTS.md` already records this class
of mistake once: a guard written for a workstation became an off switch in a
container. Deleting the project skills before verifying plugin load would turn
the weekly routine into a silent no-op with no error.
