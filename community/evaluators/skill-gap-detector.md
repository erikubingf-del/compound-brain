# Evaluator Submission

## Name

`skill-gap-detector` — Generic Project Skill Gap and Discovery Evaluator

## Repo Type

Any activated repo. Language, stack, and domain agnostic.

## Objective

On session start and cron, read the project's signals, score available skills
against those signals, detect missing or stale skills, and surface
recommendations to the human via the promotion inbox.

This evaluator is the runtime engine behind skill matching. It is not specific
to any skill. It works by reading each skill's declared `Trigger Signals` and
scoring them against what it finds in the project.

It also fetches the `skill-discovery-sources` pack on cron to find new skills
published externally that may be a good fit — and proposes them the same way.

## Run Command

```bash
python3 ~/.claude/scripts/evaluate_skill_gaps.py \
  --project-dir . \
  --skill-dirs ~/.claude/skills .claude/skills ~/.agents/skills \
  --source-pack skill-discovery-sources \
  --stale-days 30 \
  --top-n 5
```

If the script is not yet present, approximate inline:

```bash
python3 - <<'EOF'
import os, json, re
from pathlib import Path

project_dir = Path(".")

# 1. Collect project signals
signals = set()

# File extensions
for f in project_dir.rglob("*"):
    if ".git" in f.parts or "node_modules" in f.parts: continue
    signals.add(f"ext:{f.suffix.lstrip('.')}")

# Package deps
pkg = project_dir / "package.json"
if pkg.exists():
    data = json.loads(pkg.read_text())
    for dep in list(data.get("dependencies",{}).keys()) + list(data.get("devDependencies",{}).keys()):
        signals.add(f"dep:{dep}")

# Language files
for marker, lang in [("go.mod","go"),("Cargo.toml","rust"),("pyproject.toml","python"),("requirements.txt","python")]:
    if (project_dir / marker).exists(): signals.add(f"lang:{lang}")

# 2. Score skills
skill_dirs = [
    Path.home() / ".claude/skills",
    Path(".claude/skills"),
    Path.home() / ".agents/skills",
]

active_skills = set()
skills_json = project_dir / ".brain/state/skills.json"
if skills_json.exists():
    data = json.loads(skills_json.read_text())
    for s in data.get("active", []):
        active_skills.add(s["name"] if isinstance(s, dict) else s)

results = []
for skill_dir in skill_dirs:
    if not skill_dir.exists(): continue
    for skill_path in skill_dir.iterdir():
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists(): continue
        content = skill_md.read_text()
        # Extract trigger signals block
        trigger_block = re.search(r"## Trigger Signals\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
        if not trigger_block: continue
        trigger_text = trigger_block.group(1).lower()
        score = sum(1 for sig in signals if sig.split(":",1)[-1] in trigger_text)
        if score > 0:
            results.append({"skill": skill_path.name, "score": score,
                            "active": skill_path.name in active_skills})

results.sort(key=lambda x: -x["score"])
print(json.dumps({"signals": len(signals), "matches": results[:10]}, indent=2))
EOF
```

## Metric Extraction Rule

From the run output, extract per skill:
- `skill` — skill name
- `score` — number of trigger signals matched
- `active` — whether already installed in `.brain/state/skills.json`
- `stale_days` — days since skill was last refreshed (from source pack cache)

## Keep or Discard Rule

| Condition | Signal | Runtime action |
|-----------|--------|----------------|
| `score == 0` | `skip` | No match — do not recommend |
| `score > 0` AND `active == true` AND `stale_days < 30` | `pass` | Present and fresh — no action |
| `score > 0` AND `active == true` AND `stale_days >= 30` | `stale` | Fetch source pack, propose refresh via promotion inbox |
| `score > 0` AND `active == false` | `recommend` | Add to `.brain/state/skills.json` recommended[], surface to human |
| New skill found via `skill-discovery-sources` with `score > 0` | `new` | Propose installation via promotion inbox |

Top N recommended skills (default 5) are surfaced. Lower-scoring matches
are logged to `.brain/knowledge/areas/skill-health.md` but not surfaced.

## Mutable Surfaces

- `.brain/state/skills.json` — `recommended[]` only (never `active[]` without approval)
- `.brain/state/source-pack-cache.json` — last-fetched timestamps
- `.brain/knowledge/areas/skill-health.md` — audit log

## Protected Surfaces

- Any installed skill file — never auto-modified
- `.brain/state/skills.json` `active[]` — human approval required
- All project source files — this evaluator is read-only

## Runtime Budget

- Session start: max 10s — file scan + skills.json read only, no HTTP
- Cron: max 60s — includes HTTP fetches from skill-discovery-sources

## Failure Classes

- **Missing `.brain/`** — skip, do not scaffold
- **No skill directories found** — log warning, continue
- **Malformed SKILL.md** — skip that skill, log to skill-health.md
- **HTTP failure on source pack** — log, mark cache stale, continue
- **Budget exceeded** — emit `timeout`, skip remaining, never block session

## Evidence

- Pattern generalized from the CRM repo (Next.js 16 SaaS). Running against that
  repo would score `ui-master` highly from `.tsx` file presence and `tailwindcss`
  dep — without the evaluator being told anything about UI explicitly.
- Same evaluator running against a Python ML repo would score data-science skills
  from `pyproject.toml` and `requirements.txt` containing `torch`, `pandas`, etc.
- Running against a Go microservice would score API/observability skills from
  `go.mod` and the presence of `*_test.go` files.
