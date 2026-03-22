# Source Pack Submission

## Name

`ui-master-sources` — Frontend UI Inspiration and Reference Pack

## Department

engineering, product

## Objective

Provide the runtime with a curated, bounded set of approved external sources
for auditing and improving the `ui-master` skill. On session start and cron,
these sources are checked for new patterns. If newer or better-quality
guidelines exist, a skill improvement is proposed via the promotion inbox —
never applied silently.

This pack constrains research to high-signal, authoritative sources only.
It is not a broad web search.

## Approved Sources

- `https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md`
  — Vercel Web Interface Guidelines (Phase 4 of the ui-master pipeline)
- `https://ui.shadcn.com/docs` — shadcn/ui component system (patterns and accessibility)
- `https://www.radix-ui.com/primitives/docs/overview/introduction` — Radix UI
  accessibility and interaction primitives
- `https://lucide.dev/guide/packages/lucide-react` — Lucide icon system (icon-set standard)
- `https://tailwindcss.com/docs/responsive-design` — Tailwind responsive system
- `https://motion.dev/docs/react-quick-start` — Motion library (React animation patterns)
- `https://www.w3.org/WAI/WCAG21/quickref/` — WCAG 2.1 AA accessibility reference

## Search Queries

When the cron audits this pack, it should check for:
- New WCAG guidelines or contrast requirements
- Updated Vercel Web Interface Guidelines (check `Last-Modified` header)
- New Radix or shadcn accessibility patterns
- Breaking changes in Motion library API

## Recency Policy

- Vercel guidelines: check on every weekly cron run
- shadcn/Radix: check monthly
- WCAG: check quarterly
- Flag any source returning HTTP 404 or 301 — the URL may have moved

## Validation Policy

- Never apply source content directly to the skill — propose a diff via the promotion inbox
- Human approval required before any skill content changes
- If a source contradicts current skill rules, surface both and ask for resolution
- Discard sources returning non-200 status or malformed content

## Disallowed Sources

- Any AI-generated design pattern site (no verified authorship)
- Social aggregators (Dribbble, Awwwards) — inspiration only, not rule-making
- Paid design system docs behind authentication walls
- Any source not on this list — add here first before using in research

## Anti-goals

- Not a web scraper — fetch only stable, versioned docs URLs
- Not for brand identity decisions — those belong to the project, not this pack
- Not for component implementation — only for guidelines and rules

## Why This Pack Helps

UI best practices change. WCAG versions update. Libraries deprecate APIs.
Without this pack, the `ui-master` skill becomes stale silently. With it,
the cron surfaces changes to the human before they cause regressions —
accessibility failures, broken animations, deprecated icon sets.
