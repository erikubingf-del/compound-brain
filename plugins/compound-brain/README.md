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

Verified against the official docs on 2026-08-19
([discover-plugins](https://code.claude.com/docs/en/discover-plugins)):

```
/plugin marketplace add erikubingf-del/compound-brain
/plugin install compound-brain@compound-brain
```

At the install prompt, pick a scope:

- **User scope** — loads these skills in **every** project on the machine.
  This is the scope that makes the brain's capabilities ambient.
- **Project scope** — writes the plugin into that repo's
  `.claude/settings.json` (`enabledPlugins`), which is the documented path
  for cloud sessions where `/plugin` isn't available. Use this in the brain
  repo itself so scheduled cloud runs load the plugin.

**Update cadence, resolved:** Claude Code refreshes marketplaces and updates
installed plugins in the background after session start; updated plugins load
on next launch or via `/reload-plugins`. Third-party marketplaces like this
one have auto-update **disabled by default** — enable it once per machine via
`/plugin` → Marketplaces → compound-brain → **Enable auto-update**. Combined
with the omitted `version` (commit SHA = version), every push then propagates
on its own. Without auto-update, three steps:
`/plugin marketplace update compound-brain` (catalog refresh only), then
`/plugin update compound-brain@compound-brain` (updates the installed
plugin — [plugin update](https://code.claude.com/docs/en/plugins-reference#plugin-update)),
then `/reload-plugins`.
([auto-updates](https://code.claude.com/docs/en/discover-plugins#configure-auto-updates))

**Fallback without plugin machinery:** `.claude/skills/` inside a directory
passed to `--add-dir` is loaded automatically, with live reload — so
`claude --add-dir /path/to/compound-brain` picks these up per-invocation.
The `permissions.additionalDirectories` setting grants file access only and
does **not** load skills.
([additional directories](https://code.claude.com/docs/en/skills#skills-from-additional-directories))

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
