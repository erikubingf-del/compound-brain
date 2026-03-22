# Skill Submission — ui-master

## Name

`ui-master` — Consolidated UI Design Intelligence

## Goal

Produce the highest-quality, most distinctive, production-grade UI for any
frontend request. Combines design thinking (Anthropic frontend-design),
data-backed design system generation (ui-ux-pro-max), implementation standards,
and Vercel Web Interface Guidelines into a single 4-phase pipeline.

Prevents the most common failure modes of AI-generated UI: generic aesthetics,
poor accessibility, broken dark mode, and unsafe interaction patterns.

## Best Fit

- **Repo types:** Next.js, React, SaaS frontend, landing page, dashboard, CRM,
  admin panel, any project with `.tsx`/`.jsx` components or HTML/CSS output
- **Departments:** engineering, product
- **Depth range:** 2–5 (planning-only at depth 2 produces design direction;
  execution at depth 3+ produces code)

## Trigger Signals

- `.tsx`, `.jsx`, `.html`, or `.css` files present in the repo
- Dependencies: `react`, `next`, `tailwindcss`, `@shadcn/ui`, or any UI framework
- User request contains: "design", "UI", "UX", "layout", "style", "look",
  "theme", "interface", "component", "frontend", "landing page", "dashboard"
- User asks to build, create, implement, review, or improve any:
  - website, page, or web app
  - email template (HTML, newsletter, transactional)
  - UI component (button, form, card, modal, navbar, sidebar, hero)

## Inputs Required

- Product type or domain (e.g., CRM, SaaS, e-commerce, portfolio)
- Target stack (React/Next.js, plain HTML/Tailwind, Vue, Svelte, etc.)
- Aesthetic intent if provided (tone, mood, reference)
- Whether email output is needed (switches to email-safe implementation rules)

## Process

### Phase 1 — Design Thinking

Before writing any code, commit to a clear aesthetic direction:

1. Define **purpose** — what problem this interface solves and who uses it
2. Choose **tone** — commit to an extreme:
   `brutally minimal` / `maximalist chaos` / `retro-futuristic` / `organic` /
   `luxury/refined` / `playful` / `editorial` / `brutalist` / `art deco` /
   `soft/pastel` / `industrial`
3. Define **differentiation** — what makes this unforgettable vs generic AI output

**Hard rules (never break):**
- Never use purple gradients on white backgrounds
- Never default to Space Grotesk, Inter, Roboto, or Arial
- Never use timid, evenly distributed color palettes — use dominant + sharp accent
- Match code complexity to aesthetic (maximalist = elaborate animations;
  minimalist = precision in spacing)

### Phase 2 — Design System Generation

Run the ui-ux-pro-max design system script to get data-backed recommendations
for: pattern, style, colors, typography, effects, and anti-patterns.

Query by product type, industry, and keywords. Apply results to inform the
implementation choices in Phase 3.

**Rule priorities (always apply):**
1. **Accessibility (CRITICAL)** — 4.5:1 contrast, visible focus rings, aria-labels,
   keyboard nav, form labels
2. **Touch & Interaction (CRITICAL)** — 44×44px min touch targets, loading states
   on async buttons, `cursor-pointer` on all clickables
3. **Performance (HIGH)** — WebP + srcset + lazy loading, reserve space for async
4. **Layout & Responsive (HIGH)** — viewport meta, 16px min body on mobile,
   no horizontal scroll
5. **Typography & Color (MEDIUM)** — 1.5–1.75 line-height, 65–75 chars/line,
   font personality match
6. **Animation (MEDIUM)** — 150–300ms micro-interactions, transform/opacity only
7. **No emoji icons** — always SVG (Heroicons, Lucide, Simple Icons)

### Phase 3 — Implementation

Non-negotiable implementation rules:

- SVG icons only, consistent set (Heroicons or Lucide), fixed viewBox 24×24
- `cursor-pointer` on every clickable element
- Hover states: color, shadow, or border change — never layout shift
- `transition-colors duration-200` as baseline
- Light mode: `bg-white/80` minimum opacity, body text `#0F172A` minimum,
  borders `border-gray-200`
- Floating navbars: `top-4 left-4 right-4`, account for fixed height in padding
- Consistent `max-w-6xl` or `max-w-7xl` containers

**For email output only:**
- Table-based layout (Outlook compatibility)
- Inline CSS only — no `<style>` in `<head>`
- Max 600px width, web-safe font fallbacks
- No JS, no video, no CSS animations
- `alt` on every `<img>`

### Phase 4 — Vercel Web Interface Guidelines Audit

After implementation, retrieve and apply Vercel Web Interface Guidelines.
Report any violations in `file:line` format.

Always check:
- Semantic HTML and heading hierarchy
- ARIA usage correctness
- Focus management
- Keyboard accessibility
- Virtualization for long lists

### Pre-Delivery Checklist

Aesthetics: distinctive direction, characterful fonts, strong palette, orchestrated motion
Visual: SVG icons only, consistent icon set, no layout shift on hover
Interaction: cursor-pointer, hover feedback, 150–300ms transitions, focus states, disabled during async
Contrast: 4.5:1 text ratio, visible glass/transparent elements, visible borders in light mode
Layout: responsive at 375/768/1024/1440px, no horizontal scroll, consistent containers
Accessibility: alt text, labeled inputs, not color-only, reduced-motion, semantic HTML

## Validation Path

- Typecheck must pass after implementation (`tsc --noEmit`)
- No console errors in the browser
- Lighthouse accessibility score ≥ 90
- Manual check: tab through the interface — all interactive elements reachable

## Failure Modes

- Skipping Phase 1 produces generic AI output — the pipeline only works if
  design direction is committed to before code starts
- Using only ui-ux-pro-max without the Vercel audit misses accessibility gaps
- Applying email rules to web output (or vice versa) breaks layout
- Running Phase 2 search with vague keywords returns low-quality design system
  recommendations — be specific about product type and domain

## Anti-goals

- Not for CLI tools, scripts, or any non-visual output
- Not a substitute for a full design system when one already exists in the repo
  — in that case, read the existing system first and extend it
- Not for microservices, API routes, or backend-only work

## Compatibility

This skill is tool-agnostic — it contains no tool-specific API calls and works
as plain instructions with any LLM coding assistant that supports skill loading.

| Tool | Skill path | Notes |
|------|-----------|-------|
| **Claude Code** | `~/.claude/skills/ui-master/` | Loaded automatically via `SKILL.md` frontmatter |
| **Codex** | `~/.agents/skills/ui-master/` | Symlink from `~/.codex/skills/ui-master/` |
| **OpenCode** | `~/.config/opencode/skills/ui-master/` | Loaded via native `skill` tool |
| **Project-local (any tool)** | `.claude/skills/ui-master/` or `.opencode/skills/ui-master/` | Takes precedence over global — use when you want a repo-specific variant |

**Installation (Claude Code):**
```bash
cp -r community/skills/ui-master ~/.claude/skills/ui-master
```

**Installation (Codex):**
```bash
mkdir -p ~/.agents/skills
cp -r community/skills/ui-master ~/.agents/skills/ui-master
```

**Installation (OpenCode):**
```bash
cp -r community/skills/ui-master ~/.config/opencode/skills/ui-master
```

**Project-local (any tool):**
```bash
mkdir -p .claude/skills   # or .opencode/skills
cp -r community/skills/ui-master .claude/skills/ui-master
```

Project-local always wins. Use it when the global skill needs repo-specific
overrides (different tone defaults, different stack, company-specific rules).

## Evidence

- **Repo:** `/Users/erikfigueiredo/crm` — Next.js 16 SaaS CRM
- **Before:** UI components used Inter font, flat color cards, no design token
  discipline, inconsistent hover states, missing accessibility attributes
- **After:** Committed to luxury/refined tone with characterful font pairings,
  dominant color + sharp accent system, all interactive elements have
  cursor-pointer and hover feedback, focus rings present, 4.5:1 contrast
  enforced, dark mode glass elements use minimum 80% opacity
- **Qualitative improvement:** Design review feedback shifted from "generic AI"
  to "could be a real product" — CRM passed visual inspection for investor demo
