from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import re
from pathlib import Path
from typing import Any

try:
    from scripts.lib.skill_evolution import slugify, upsert_skill_pattern
except ModuleNotFoundError:
    from lib.skill_evolution import slugify, upsert_skill_pattern


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def claude_home_dir() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".claude"


def default_approved_external_skill_roots() -> list[Path]:
    override = os.environ.get("COMPOUND_BRAIN_APPROVED_SKILL_DIRS")
    if override:
        return [Path(item).expanduser() for item in override.split(os.pathsep) if item]

    roots = []
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    roots.append(codex_home / "skills")
    roots.append(Path.home() / ".agents" / "skills")
    return roots


def normalize_tokens(*parts: str) -> set[str]:
    text = " ".join(parts).lower()
    stopwords = {
        "and",
        "are",
        "for",
        "from",
        "into",
        "key",
        "knowledge",
        "level",
        "needs",
        "next",
        "none",
        "project",
        "projects",
        "related",
        "repo",
        "skill",
        "the",
        "this",
        "update",
    }
    tokens = {
        token
        for token in re.split(r"[^a-z0-9]+", text)
        if len(token) > 1 and token not in stopwords
    }
    aliases = {
        "ui": {"frontend", "design"},
        "frontend": {"ui"},
        "deploy": {"deployment", "release", "operations"},
        "release": {"deploy", "operations"},
        "research": {"experiment", "evaluation", "autoresearch"},
        "debugging": {"reliability", "fix"},
        "docs": {"documentation", "product"},
        "documentation": {"docs", "product"},
        "react": {"frontend", "ui"},
        "next": {"frontend", "ui"},
        "typescript": {"frontend", "engineering"},
        "python": {"backend", "service"},
        "backend": {"api", "service"},
        "tests": {"testing", "validation"},
        "testing": {"tests", "validation"},
    }
    expanded = set(tokens)
    for token in list(tokens):
        expanded.update(aliases.get(token, set()))
    return expanded


def enabled_departments(project_dir: Path) -> list[str]:
    settings_path = project_dir / ".claude" / "settings.local.json"
    if settings_path.exists():
        settings = json.loads(settings_path.read_text())
        departments = settings.get("enabledDepartments")
        if isinstance(departments, list) and departments:
            return [str(item) for item in departments]
    departments_dir = project_dir / ".claude" / "departments"
    if departments_dir.exists():
        return sorted(path.stem for path in departments_dir.glob("*.md"))
    return []


def detect_stack_tokens(project_dir: Path) -> set[str]:
    tokens: set[str] = set()
    checks = {
        "python": ["pyproject.toml", "requirements.txt", "setup.py"],
        "typescript": ["tsconfig.json"],
        "javascript": ["package.json"],
        "next": ["next.config.js", "next.config.ts"],
        "react": ["src/App.tsx", "src/App.jsx", "app/page.tsx"],
        "go": ["go.mod"],
        "rust": ["Cargo.toml"],
        "docker": ["Dockerfile", "docker-compose.yml"],
    }
    for token, markers in checks.items():
        if any((project_dir / marker).exists() for marker in markers):
            tokens.add(token)

    if any(project_dir.rglob("*.tsx")) or any(project_dir.rglob("*.jsx")):
        tokens.update({"react", "frontend", "ui"})
    if (project_dir / "tests").exists() or (project_dir / "test").exists():
        tokens.update({"testing", "validation"})
    if (project_dir / ".github" / "workflows").exists():
        tokens.update({"ci", "release", "operations"})
    if (project_dir / ".brain" / "autoresearch" / "program.md").exists():
        tokens.update({"research", "experiment", "autoresearch"})
    if (project_dir / "README.md").exists():
        tokens.update({"docs", "documentation", "product"})
    return tokens


def infer_required_capabilities(project_dir: Path, departments: list[str] | None = None) -> list[dict[str, Any]]:
    departments = departments or enabled_departments(project_dir)
    stack = detect_stack_tokens(project_dir)
    capabilities: list[dict[str, Any]] = []

    def add(
        title: str,
        department: str,
        reason: str,
        keywords: list[str],
        priority: int,
    ) -> None:
        capabilities.append(
            {
                "id": slugify(title),
                "title": title,
                "department": department,
                "reason": reason,
                "priority": priority,
                "keywords": sorted(normalize_tokens(title, department, reason, *keywords)),
            }
        )

    if "architecture" in departments:
        add(
            "Architecture Governance",
            "architecture",
            "The repo needs architecture guidance, control-plane consistency, and bounded autonomy rules.",
            ["architecture", "orchestration", "control", "decision", "approval"],
            7,
        )
    if "engineering" in departments:
        add(
            "Debugging Reliability",
            "engineering",
            "Engineering needs repeatable debugging, reliability, and repair discipline.",
            ["debugging", "reliability", "engineering", "fix", "quality"],
            8,
        )
    if "operations" in departments or {"release", "operations", "ci"} & stack:
        add(
            "Release Operations",
            "operations",
            "Operations surfaces need deploy, release, and runtime safety coverage.",
            ["deploy", "release", "operations", "ci", "runtime"],
            8,
        )
    if "research" in departments or {"research", "experiment", "autoresearch"} & stack:
        add(
            "Experiment Evaluation",
            "research",
            "Research loops need evaluators, experiments, and keep/discard discipline.",
            ["research", "experiment", "evaluation", "autoresearch", "hypothesis"],
            6,
        )
    if "product" in departments or {"docs", "documentation", "product"} & stack:
        add(
            "Product Documentation",
            "product",
            "The repo needs product intent, docs, and clear user-facing direction.",
            ["product", "documentation", "docs", "requirements", "content"],
            7,
        )
    if {"frontend", "ui", "react", "next"} & stack:
        add(
            "Frontend UI",
            "engineering",
            "Frontend-facing repos need UI, design, and interaction skills.",
            ["frontend", "ui", "design", "react", "next"],
            9,
        )
    if {"python", "go", "javascript"} & stack:
        add(
            "Backend Services",
            "engineering",
            "The repo needs backend service and API implementation discipline.",
            ["backend", "api", "service", "python", "go", "node"],
            8,
        )
    if {"testing", "validation"} & stack:
        add(
            "Test Automation",
            "engineering",
            "The repo should keep validation and test automation current.",
            ["test", "testing", "validation", "qa"],
            8,
        )
    return capabilities


def parse_skill_graph(skills_dir: Path, source: str) -> list[dict[str, Any]]:
    graph_path = skills_dir / "skill-graph.md"
    if not graph_path.exists():
        return []

    skills: list[dict[str, Any]] = []
    current_title: str | None = None
    current_lines: list[str] = []
    description = ""
    next_improvements = ""

    def flush() -> None:
        if not current_title:
            return
        if current_title in {"Template", "Skill Name"}:
            return
        slug = slugify(current_title)
        pattern_path = skills_dir / "patterns" / f"{slug}.md"
        pattern_body = pattern_path.read_text() if pattern_path.exists() else ""
        skills.append(
            {
                "title": current_title,
                "slug": slug,
                "description": description or "Project skill entry.",
                "next_improvements": next_improvements,
                "source": source,
                "source_path": str(pattern_path if pattern_path.exists() else graph_path),
                "pattern_body": pattern_body,
                "tokens": sorted(
                    normalize_tokens(current_title, description, next_improvements, " ".join(current_lines))
                ),
            }
        )

    for raw_line in graph_path.read_text().splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            flush()
            current_title = line[3:].strip()
            current_lines = []
            description = ""
            next_improvements = ""
            continue
        if current_title:
            current_lines.append(line)
            if line.startswith("**Key Knowledge:**"):
                description = line.split(":", 1)[1].strip()
            elif line.startswith("**Next Improvements:**"):
                next_improvements = line.split(":", 1)[1].strip()
    flush()
    return skills


def parse_frontmatter(path: Path) -> tuple[str, str]:
    text = path.read_text()
    title = path.parent.name
    description = ""
    match = re.match(r"---\n(.*?)\n---\n?", text, re.DOTALL)
    if match:
        body = match.group(1)
        name_match = re.search(r"^name:\s*(.+)$", body, re.MULTILINE)
        desc_match = re.search(r'^description:\s*"?(.*?)"?$', body, re.MULTILINE)
        if name_match:
            title = name_match.group(1).strip()
        if desc_match:
            description = desc_match.group(1).strip()
    if not description:
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                title = stripped[2:].strip()
                continue
            if stripped and not stripped.startswith("---"):
                description = stripped
                break
    return title, description or "External skill reference."


def parse_external_skills(roots: list[Path]) -> list[dict[str, Any]]:
    skills: list[dict[str, Any]] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("SKILL.md")):
            title, description = parse_frontmatter(path)
            skills.append(
                {
                    "title": title,
                    "slug": slugify(title),
                    "description": description,
                    "next_improvements": "Adapt to the repo's local control plane.",
                    "source": "external",
                    "source_path": str(path),
                    "pattern_body": path.read_text(),
                    "tokens": sorted(normalize_tokens(title, description, str(path.parent.name))),
                }
            )
    return skills


def score_skill(capability: dict[str, Any], skill: dict[str, Any]) -> int:
    capability_tokens = set(capability["keywords"])
    skill_tokens = set(skill["tokens"])
    score = len(capability_tokens & skill_tokens)
    if capability["department"] in skill_tokens:
        score += 1
    if capability["id"] == skill["slug"]:
        score += 2
    return score


EXTERNAL_TITLE_HINTS = {
    "architecture-governance": {"brainstorming", "writing", "plans", "review"},
    "debugging-reliability": {"debugging", "verification", "test", "checks"},
    "release-operations": {"verification", "commit", "deploy", "release"},
    "experiment-evaluation": {"autoresearch", "experiment", "evaluation"},
    "product-documentation": {"prd", "documentation", "product", "content"},
    "frontend-ui": {"ui", "frontend", "design", "web"},
    "backend-services": {"backend", "api", "service"},
    "test-automation": {"test", "verification", "checks"},
}


def external_match_allowed(capability: dict[str, Any], skill: dict[str, Any]) -> bool:
    if skill["source"] != "external":
        return True
    allowed = EXTERNAL_TITLE_HINTS.get(capability["id"], set())
    title_tokens = set(normalize_tokens(skill["title"], skill["slug"]))
    return bool(title_tokens & allowed)


def match_capability(
    capability: dict[str, Any],
    skills: list[dict[str, Any]],
    exclude_slugs: set[str] | None = None,
) -> dict[str, Any] | None:
    exclude_slugs = exclude_slugs or set()
    ranked: list[tuple[int, dict[str, Any]]] = []
    for skill in skills:
        if skill["slug"] in exclude_slugs:
            continue
        if not external_match_allowed(capability, skill):
            continue
        score = score_skill(capability, skill)
        if score <= 0:
            continue
        ranked.append((score, skill))
    if not ranked:
        return None
    ranked.sort(key=lambda item: (item[0], item[1]["title"]), reverse=True)
    score, skill = ranked[0]
    return {
        "capability": capability["title"],
        "score": score,
        "title": skill["title"],
        "slug": skill["slug"],
        "description": skill["description"],
        "source": skill["source"],
        "source_path": skill["source_path"],
        "pattern_body": skill["pattern_body"],
        "next_improvements": skill["next_improvements"],
    }


def load_local_global_external_skills(
    project_dir: Path,
    claude_home: Path,
    approved_external_roots: list[Path],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    local = parse_skill_graph(project_dir / ".brain" / "knowledge" / "skills", "repo")
    global_skills = parse_skill_graph(claude_home / "knowledge" / "skills", "global")
    external = parse_external_skills(approved_external_roots)
    return local, global_skills, external


def classify_local_skills(
    capabilities: list[dict[str, Any]],
    local_skills: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    active: list[dict[str, Any]] = []
    stale: list[dict[str, Any]] = []
    for skill in local_skills:
        ranked = sorted(
            (
                {
                    "capability": capability["title"],
                    "score": score_skill(capability, skill),
                }
                for capability in capabilities
            ),
            key=lambda item: item["score"],
            reverse=True,
        )
        matched = [item for item in ranked if item["score"] >= 2]
        record = {
            "title": skill["title"],
            "slug": skill["slug"],
            "source": skill["source"],
            "source_path": skill["source_path"],
            "matched_capabilities": [item["capability"] for item in matched],
            "score": matched[0]["score"] if matched else 0,
        }
        if matched:
            active.append(record)
        else:
            stale.append(record)
    return active, stale


def build_pattern_body(skill: dict[str, Any], capability: dict[str, Any]) -> str:
    if skill["source"] == "global" and skill.get("pattern_body"):
        body = skill["pattern_body"].rstrip() + "\n"
    else:
        body = f"# {skill['title']}\n\n{skill['description']}\n"
    return (
        body.rstrip()
        + "\n\n## Compound-Brain Match\n"
        + f"- Source: {skill['source']}\n"
        + f"- Source Path: `{skill['source_path']}`\n"
        + f"- Capability: {capability['title']}\n"
        + f"- Reason: {capability['reason']}\n"
        + "\n"
    )


def materialize_recommendations(
    project_dir: Path,
    recommendations: list[dict[str, Any]],
    capabilities_by_title: dict[str, dict[str, Any]],
    limit: int = 2,
) -> list[dict[str, Any]]:
    ranked_recommendations = sorted(
        recommendations,
        key=lambda item: (
            capabilities_by_title[item["capability"]]["priority"],
            item["score"],
            item["title"],
        ),
        reverse=True,
    )
    materialized: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    for recommendation in ranked_recommendations:
        if recommendation["source"] not in {"global", "external"}:
            continue
        if recommendation["score"] < 3:
            continue
        if recommendation["title"] in seen_titles:
            continue
        capability = capabilities_by_title[recommendation["capability"]]
        upsert_skill_pattern(
            skills_dir=project_dir / ".brain" / "knowledge" / "skills",
            skill_name=recommendation["title"],
            related_projects=[project_dir.name],
            key_knowledge=recommendation["description"],
            next_improvements=recommendation["next_improvements"],
            pattern_body=build_pattern_body(recommendation, capability),
        )
        materialized.append(
            {
                "title": recommendation["title"],
                "source": recommendation["source"],
                "capability": recommendation["capability"],
            }
        )
        seen_titles.add(recommendation["title"])
        if len(materialized) >= limit:
            break
    return materialized


def write_skill_state(project_dir: Path, payload: dict[str, Any]) -> None:
    state_path = project_dir / ".brain" / "state" / "skills.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2) + "\n")


def refresh_repo_skill_state(
    project_dir: Path,
    claude_home: Path | None = None,
    approved_external_roots: list[Path] | None = None,
) -> dict[str, Any]:
    project_dir = project_dir.resolve()
    claude_home = (claude_home or claude_home_dir()).resolve()
    approved_external_roots = approved_external_roots or default_approved_external_skill_roots()

    departments = enabled_departments(project_dir)
    capabilities = infer_required_capabilities(project_dir, departments)
    local_skills, global_skills, external_skills = load_local_global_external_skills(
        project_dir,
        claude_home,
        approved_external_roots,
    )

    active, stale = classify_local_skills(capabilities, local_skills)
    active_titles = {item["title"] for item in active}
    recommendations: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    capabilities_by_title = {item["title"]: item for item in capabilities}

    global_external = global_skills + external_skills
    for capability in capabilities:
        if capability["title"] in {cap for item in active for cap in item["matched_capabilities"]}:
            continue
        match = match_capability(
            capability,
            global_external,
            exclude_slugs={slugify(title) for title in active_titles},
        )
        if match and match["score"] >= 2:
            recommendations.append(match)
            continue
        missing.append(
            {
                "title": capability["title"],
                "department": capability["department"],
                "reason": capability["reason"],
            }
        )

    materialized = materialize_recommendations(project_dir, recommendations, capabilities_by_title)
    if materialized:
        local_skills, _, _ = load_local_global_external_skills(
            project_dir,
            claude_home,
            approved_external_roots,
        )
        active, stale = classify_local_skills(capabilities, local_skills)
        materialized_titles = {item["title"] for item in materialized}
        recommendations = [
            item for item in recommendations if item["title"] not in materialized_titles
        ]

    payload = {
        "generated_at": now_utc(),
        "repo": project_dir.name,
        "departments": departments,
        "required_capabilities": capabilities,
        "active": active,
        "recommended": [
            {
                "title": item["title"],
                "capability": item["capability"],
                "source": item["source"],
                "score": item["score"],
                "source_path": item["source_path"],
            }
            for item in recommendations
        ],
        "materialized": materialized,
        "stale": stale,
        "missing": missing,
        "inventory_counts": {
            "repo": len(local_skills),
            "global": len(global_skills),
            "external": len(external_skills),
        },
    }
    write_skill_state(project_dir, payload)
    return payload
