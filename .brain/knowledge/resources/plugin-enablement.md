# Enabling the compound-brain plugin everywhere — verified guide

**Logged:** 2026-08-19. All commands below verified against official docs:
[discover-plugins](https://code.claude.com/docs/en/discover-plugins),
[plugins](https://code.claude.com/docs/en/plugins).

The plugin is the only single artifact that covers every local project AND
cloud sessions at once (repo `.claude/skills/` covers one repo; personal
`~/.claude/skills/` never reaches cloud/routine sessions). This is the
mechanism that makes "every Claude Code project uses the latest skills"
true. Three scopes, three steps.

---

## 1. Workstation — all local projects (owner, one time)

```
/plugin marketplace add erikubingf-del/compound-brain
/plugin install compound-brain@compound-brain
```

At the install prompt choose **User scope** — that installs it for you across
**all** projects on that machine. Skills then load namespaced:
`compound-brain:brain-orient`, `compound-brain:brain-digest`, etc.
[VERIFIED: discover-plugins — "User scope: install for yourself across all projects"]

## 2. This repo's cloud/scheduled sessions (owner, one time)

Run the same two commands in an interactive session **in this repo**, but
choose **Project scope** at the install prompt. Project scope writes the
plugin into `.claude/settings.json` (`enabledPlugins`), which is the
documented path for sessions where `/plugin` isn't available — i.e. exactly
the cloud sessions the weekly routine runs in.
[VERIFIED: discover-plugins — "Project scope … adds the plugin to .claude/settings.json"; "declare the plugin under enabledPlugins in .claude/settings.json for cloud sessions"]

**Before committing, verify the settings file carries BOTH halves:** the
`enabledPlugins` entry (`compound-brain@compound-brain`) AND an
`extraKnownMarketplaces` entry declaring the marketplace source
(`github` / `erikubingf-del/compound-brain`). Cloud sessions install "from
the marketplace you declared" — an `enabledPlugins` entry alone, with no
committed marketplace declaration, may fail to resolve `@compound-brain` in
a fresh clone, which would silently reproduce the exact failure queue 009
exists to catch. If the installer wrote only `enabledPlugins`, add the
`extraKnownMarketplaces` block by hand (pattern: discover-plugins →
"Configure team marketplaces"). Then commit the settings change.

This is the unblock for queue 009 (verify plugin loads in a cloud session):
after the settings change lands on `main`, the next scheduled run should see
namespaced `compound-brain:*` skills. Only then may `.claude/skills/` be
deleted (queue 010).

## 3. Staying updated — how pushes propagate

- Version is deliberately omitted from `plugin.json` and the marketplace
  entry, so the git commit SHA is the version: **every push to this repo is a
  new plugin release.** [VERIFIED: plugins-reference — version management]
- When auto-update is enabled for a marketplace, Claude Code checks it and
  updates installed plugins in the background after session start (≤10 min
  random delay); updated plugins load next launch or via `/reload-plugins`.
  Third-party marketplaces (this one) have auto-update **disabled by
  default** — enable it per-marketplace via the `/plugin` UI (a local
  setting, so effectively once per machine):
  `/plugin` → Marketplaces → compound-brain → **Enable auto-update**.
  [VERIFIED: discover-plugins — "Configure auto-updates"]
- Without auto-update, update manually:
  `/plugin marketplace update compound-brain` (refreshes the catalog only),
  then `/plugin update compound-brain@compound-brain` (updates the installed
  plugin), then `/reload-plugins`.
  [VERIFIED: plugins-reference — "plugin update — Update a plugin to the latest version"]

## Facts that shaped this design

- Project `.claude/skills/` and personal `~/.claude/skills/` do NOT propagate:
  project skills load only in their own repo; personal skills are absent from
  cloud/routine sessions. The plugin is the only vehicle that covers both.
- Plugin skills and same-named project skills **coexist** (namespacing means
  neither overrides the other) — so while `.claude/skills/` still exists here,
  sessions in this repo see the un-namespaced copies too. Official migration
  guidance: remove the originals after the plugin is verified. That is queue
  010, gated on 009. [VERIFIED: plugins — "convert existing configurations"]
- `extraKnownMarketplaces` in project settings auto-adds the marketplace for
  anyone who trusts the repo folder, but since v2.1.195 externally-sourced
  plugins still require an explicit install per user. The two-command flow
  above is therefore the reliable path. [VERIFIED: discover-plugins — "Configure team marketplaces"]
