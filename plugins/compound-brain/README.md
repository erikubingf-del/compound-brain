# compound-brain plugin

Ships the brain's operator skills so they load in **every** project, not just
this repo.

| Skill | What it does |
|---|---|
| `brain-orient` | Read `AGENTS.md`, queue, and recent digests before acting; report pending and stale state |
| `brain-write` | Route a fact/decision/pattern to its correct home in `.brain/`; dedup, index, scrub |
| `brain-digest` | Run the weekly research digest: scan, verify against official docs, write, self-apply SAFE, push |
| `validate-digest` | Check a digest against its typed contract before commit |

Plugin components are namespaced by plugin name, so these appear as
`compound-brain:brain-orient` and cannot collide with a same-named project or
personal skill.
([plugins-reference](https://code.claude.com/docs/en/plugins-reference#plugin-manifest-schema))

## Why a plugin instead of `~/.claude/skills/`

A personal skill in `~/.claude/skills/` is not available to cloud or routine
sessions, because each such run is a fresh remote session. The weekly digest
routine *is* a remote session — so personal-scope skills would work on the
workstation and silently vanish in exactly the execution mode this system is
built around. Plugin skills load wherever the plugin is enabled.
([skills](https://code.claude.com/docs/en/skills))

## Version is omitted on purpose — do not add one

Claude Code resolves a plugin's version from the first of: `version` in
`plugin.json`, then `version` in the marketplace entry, then the git commit SHA,
then `unknown`. That version is the **cache key for updates**.

Both files here deliberately omit `version`, so the commit SHA becomes the
version and every push is a new one. Setting `version` anywhere pins consumers:
new commits do nothing and `/plugin update` reports "already at the latest
version" forever.
([version management](https://code.claude.com/docs/en/plugins-reference#version-management))

## Layout rule that breaks plugins most often

Only `plugin.json` belongs in `.claude-plugin/`. Everything else — `skills/`,
`agents/`, `hooks/`, `commands/` — lives at the **plugin root**. The official
docs state this twice, once as a warning and once in troubleshooting.
([directory structure](https://code.claude.com/docs/en/plugins-reference#plugin-directory-structure))

## Installing

Add this repo as a marketplace and enable the plugin, then it is available in
every project. Follow the current official flow at
<https://code.claude.com/docs/en/plugins> — the exact `/plugin` command syntax
and the value schema for the `extraKnownMarketplaces` setting were **not
verified** in the research run that produced this file, and this brain's
standing rule is that unverified mechanics get labelled rather than asserted.

**Verified alternative, usable right now:** `.claude/skills/` inside a
directory passed to `--add-dir` is loaded automatically, with live reload. So
`claude --add-dir /path/to/compound-brain` picks these up in any project
without any plugin machinery. Note this is a per-invocation flag, not an
architecture — and note that the `permissions.additionalDirectories` setting
grants file access only and does **not** load skills.
([additional directories](https://code.claude.com/docs/en/skills#skills-from-additional-directories))

**Update cadence is an open question.** Verified: version resolution and that
version is the update cache key. Not verified: whether enabled plugins pull new
commits on their own. Treat updating as an explicit step until confirmed.

## These skills check their scope

Because a plugin loads everywhere, each skill checks whether the current
project actually has a `.brain/` tree before doing anything, and stops with a
plain explanation if not. A skill that silently creates an empty brain in an
unrelated repo would look like memory while holding none — worse than no skill.

## What must never go in here

`plugins/**` is world-readable and installs into every project where it is
enabled. It is a published surface, not memory. Private brain content, project
names, hosts, and strategy details stay in `.brain/` — and, since this repo is
public, out of both.
