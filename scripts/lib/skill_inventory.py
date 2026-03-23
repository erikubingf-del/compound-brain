from __future__ import annotations

from datetime import datetime, timezone
from fnmatch import fnmatch
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


def days_since(timestamp: float) -> int:
    delta = datetime.now(timezone.utc).timestamp() - timestamp
    return max(int(delta // 86400), 0)


def parse_sectioned_markdown(path: Path) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = "root"
    sections[current] = []
    for raw_line in path.read_text().splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("## "):
            current = stripped[3:].strip().lower()
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(raw_line.rstrip())
    return sections


def parse_department_source_pack(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "objective": "",
            "approved_sources": [],
            "search_queries": [],
            "validation_policy": [],
            "anti_goals": [],
        }
    sections = parse_sectioned_markdown(path)

    def list_items(name: str) -> list[str]:
        values = []
        for line in sections.get(name, []):
            stripped = line.strip()
            if stripped.startswith("- "):
                values.append(stripped[2:].strip())
        return values

    return {
        "objective": " ".join(list_items("objective")),
        "approved_sources": list_items("approved sources"),
        "search_queries": list_items("search queries"),
        "validation_policy": list_items("validation policy"),
        "anti_goals": list_items("anti-goals"),
    }


def load_department_source_packs(project_dir: Path, departments: list[str]) -> dict[str, dict[str, Any]]:
    knowledge_dir = project_dir / ".brain" / "knowledge" / "departments"
    return {
        department: parse_department_source_pack(knowledge_dir / f"{department}-sources.md")
        for department in departments
    }


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
                "freshness_days": days_since(
                    (pattern_path if pattern_path.exists() else graph_path).stat().st_mtime
                ),
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
                    "freshness_days": days_since(path.stat().st_mtime),
                    "tokens": sorted(normalize_tokens(title, description, str(path.parent.name))),
                }
            )
    return skills


def parse_radar_skills(catalog_path: Path) -> tuple[list[dict[str, Any]], int, str | None]:
    if not catalog_path.exists():
        return [], 0, None
    payload = json.loads(catalog_path.read_text())
    skills: list[dict[str, Any]] = []
    for candidate in payload.get("candidates", []):
        title = str(candidate.get("title") or candidate.get("source_name") or "external-candidate")
        summary = str(candidate.get("summary") or candidate.get("candidate_tip") or "External radar candidate.")
        hints = [
            *[str(item) for item in candidate.get("department_hints", [])],
            *[str(item) for item in candidate.get("capability_hints", [])],
            str(candidate.get("source_name") or ""),
            str(candidate.get("candidate_tip") or ""),
        ]
        skills.append(
            {
                "title": title,
                "slug": slugify(title),
                "description": summary,
                "next_improvements": f"Adapt {title} to the repo control plane with validation.",
                "source": "radar",
                "source_path": str(candidate.get("source_url") or candidate.get("source_name") or catalog_path),
                "pattern_body": "",
                "freshness_days": int(candidate.get("freshness_days", 9999)),
                "tokens": sorted(normalize_tokens(title, summary, *hints)),
                "source_trust": float(candidate.get("source_trust", 0.82)),
                "confidence": float(candidate.get("confidence", 0.75)),
                "candidate_tip": str(candidate.get("candidate_tip") or ""),
            }
        )
    return skills, int(payload.get("version", 0)), payload.get("generated_at")


def parse_project_tip_catalog(
    catalog_path: Path,
    *,
    repo_name: str,
) -> tuple[list[dict[str, Any]], int]:
    if not catalog_path.exists():
        return [], 0
    payload = json.loads(catalog_path.read_text())
    tips = []
    for tip in payload.get("tips", []):
        source_repo = str(tip.get("source_repo") or "")
        tip_payload = {
            "id": str(tip.get("id") or ""),
            "source_repo": source_repo,
            "department": str(tip.get("department") or ""),
            "capability": str(tip.get("capability") or ""),
            "tip": str(tip.get("tip") or ""),
            "evidence_count": int(tip.get("evidence_count", 1)),
            "success_count": int(tip.get("success_count", 0)),
            "failure_count": int(tip.get("failure_count", 0)),
            "promotion_level": str(tip.get("promotion_level") or "local-tip"),
            "confidence": float(tip.get("confidence", 0.6)),
            "is_local": source_repo == repo_name,
        }
        tips.append(tip_payload)
    return tips, int(payload.get("version", 0))


def load_external_intelligence(
    claude_home: Path,
    *,
    repo_name: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int], str | None]:
    resources_dir = claude_home / "knowledge" / "resources"
    radar_skills, skill_catalog_version, generated_at = parse_radar_skills(
        resources_dir / "skill-catalog.json"
    )
    project_tips, tip_catalog_version = parse_project_tip_catalog(
        resources_dir / "project-tip-catalog.json",
        repo_name=repo_name,
    )
    versions = {
        "skill_catalog": skill_catalog_version,
        "project_tip_catalog": tip_catalog_version,
    }
    return radar_skills, project_tips, versions, generated_at


def source_trust(skill: dict[str, Any]) -> float:
    source = str(skill.get("source", "external"))
    if source == "repo":
        return 1.0
    if source == "global":
        return 0.9
    if source == "radar":
        return float(skill.get("source_trust", 0.82))
    return 0.75


def source_pack_tokens(source_pack: dict[str, Any]) -> set[str]:
    return normalize_tokens(
        source_pack.get("objective", ""),
        " ".join(source_pack.get("approved_sources", [])),
        " ".join(source_pack.get("search_queries", [])),
    )


def score_skill(
    capability: dict[str, Any],
    skill: dict[str, Any],
    source_pack: dict[str, Any] | None = None,
) -> tuple[int, list[str]]:
    capability_tokens = set(capability["keywords"])
    skill_tokens = set(skill["tokens"])
    source_pack = source_pack or {}
    query_tokens = source_pack_tokens(source_pack)

    overlap = capability_tokens & skill_tokens
    score = len(overlap)
    reasons = []
    if overlap:
        reasons.append(f"capability overlap: {', '.join(sorted(overlap)[:4])}")
    if capability["department"] in skill_tokens:
        score += 1
        reasons.append(f"department match: {capability['department']}")
    if capability["id"] == skill["slug"]:
        score += 2
        reasons.append("exact capability slug match")
    query_overlap = query_tokens & skill_tokens
    if query_overlap:
        score += min(len(query_overlap), 2)
        reasons.append(f"source-pack overlap: {', '.join(sorted(query_overlap)[:4])}")
    freshness_days = int(skill.get("freshness_days", 9999))
    if freshness_days <= 30:
        reasons.append("recent skill evidence")
    if source_trust(skill) >= 0.9:
        reasons.append("trusted source")
    return score, reasons


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
    if skill["source"] not in {"external", "radar"}:
        return True
    allowed = EXTERNAL_TITLE_HINTS.get(capability["id"], set())
    skill_tokens = set(skill.get("tokens", []))
    if skill["source"] == "external":
        skill_tokens |= set(normalize_tokens(skill["title"], skill["slug"]))
    return bool(skill_tokens & allowed)


def project_tip_bonus(
    capability: dict[str, Any],
    skill: dict[str, Any],
    project_tips: list[dict[str, Any]] | None,
) -> tuple[int, list[str]]:
    if not project_tips:
        return 0, []

    capability_tokens = set(capability["keywords"])
    skill_tokens = set(skill.get("tokens", []))
    best_bonus = 0
    best_reason = ""
    for tip in project_tips:
        if tip.get("department") != capability["department"] and tip.get("capability") != capability["id"]:
            continue
        tip_tokens = normalize_tokens(str(tip.get("tip", "")), str(tip.get("capability", "")))
        overlap = len((capability_tokens | skill_tokens) & tip_tokens)
        if overlap == 0:
            continue
        bonus = min(3, int(tip.get("evidence_count", 1)))
        if tip.get("is_local"):
            bonus += 1
        if bonus > best_bonus:
            best_bonus = bonus
            best_reason = f"project tip evidence: {str(tip.get('tip', ''))[:120]}"
    return best_bonus, ([best_reason] if best_reason else [])


def match_capability(
    capability: dict[str, Any],
    skills: list[dict[str, Any]],
    source_pack: dict[str, Any] | None = None,
    exclude_slugs: set[str] | None = None,
    project_tips: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    exclude_slugs = exclude_slugs or set()
    ranked: list[tuple[int, dict[str, Any], list[str]]] = []
    for skill in skills:
        if skill["slug"] in exclude_slugs:
            continue
        if not external_match_allowed(capability, skill):
            continue
        score, reasons = score_skill(capability, skill, source_pack=source_pack)
        tip_bonus, tip_reasons = project_tip_bonus(capability, skill, project_tips)
        score += tip_bonus
        reasons.extend(tip_reasons)
        if score <= 0:
            continue
        ranked.append((score, skill, reasons))
    if not ranked:
        return None
    ranked.sort(key=lambda item: (item[0], source_trust(item[1]), item[1]["title"]), reverse=True)
    score, skill, reasons = ranked[0]
    adaptation_notes = [
        f"Adapt `{skill['title']}` to the `{capability['department']}` department in `{capability['title']}`.",
    ]
    if source_pack:
        if source_pack.get("objective"):
            adaptation_notes.append(f"Department objective: {source_pack['objective']}")
        queries = source_pack.get("search_queries", [])
        if queries:
            adaptation_notes.append(f"Search focus: {', '.join(queries[:2])}")
    return {
        "capability": capability["title"],
        "department": capability["department"],
        "score": score,
        "title": skill["title"],
        "slug": skill["slug"],
        "description": skill["description"],
        "source": skill["source"],
        "source_path": skill["source_path"],
        "pattern_body": skill["pattern_body"],
        "next_improvements": skill["next_improvements"],
        "freshness_days": int(skill.get("freshness_days", 9999)),
        "source_trust": source_trust(skill),
        "match_reasons": reasons,
        "adaptation_notes": adaptation_notes,
    }


def load_local_global_external_skills(
    project_dir: Path,
    claude_home: Path,
    approved_external_roots: list[Path],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, int],
    str | None,
]:
    local = parse_skill_graph(project_dir / ".brain" / "knowledge" / "skills", "repo")
    global_skills = parse_skill_graph(claude_home / "knowledge" / "skills", "global")
    external = parse_external_skills(approved_external_roots)
    radar_skills, project_tips, catalog_versions, external_generated_at = load_external_intelligence(
        claude_home,
        repo_name=project_dir.name,
    )
    return (
        local,
        global_skills,
        external,
        radar_skills,
        project_tips,
        catalog_versions,
        external_generated_at,
    )


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
                    "score": score_skill(capability, skill)[0],
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


def build_pattern_body(
    project_dir: Path,
    skill: dict[str, Any],
    capability: dict[str, Any],
    source_pack: dict[str, Any] | None = None,
) -> str:
    if skill["source"] == "global" and skill.get("pattern_body"):
        body = skill["pattern_body"].rstrip() + "\n"
    else:
        body = f"# {skill['title']}\n\n{skill['description']}\n"
    source_pack = source_pack or {}
    search_queries = source_pack.get("search_queries", [])
    return (
        body.rstrip()
        + "\n\n## Compound-Brain Match\n"
        + f"- Source: {skill['source']}\n"
        + f"- Source Path: `{skill['source_path']}`\n"
        + f"- Capability: {capability['title']}\n"
        + f"- Reason: {capability['reason']}\n"
        + f"- Department: {capability['department']}\n"
        + "\n## Repo Adaptation\n"
        + f"- Repo: `{project_dir.name}`\n"
        + f"- Department objective: {source_pack.get('objective', 'Pending department objective.')}\n"
        + (
            f"- Search queries: {', '.join(search_queries[:2])}\n"
            if search_queries
            else "- Search queries: none captured\n"
        )
        + f"- Adaptation notes: {' | '.join(skill.get('adaptation_notes', []))}\n"
        + "\n"
    )


def materialize_recommendations(
    project_dir: Path,
    recommendations: list[dict[str, Any]],
    capabilities_by_title: dict[str, dict[str, Any]],
    source_packs: dict[str, dict[str, Any]],
    limit: int = 3,
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
        if recommendation["source"] not in {"global", "external", "radar"}:
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
            pattern_body=build_pattern_body(
                project_dir,
                recommendation,
                capability,
                source_pack=source_packs.get(capability["department"], {}),
            ),
        )
        materialized.append(
            {
                "title": recommendation["title"],
                "source": recommendation["source"],
                "capability": recommendation["capability"],
                "department": capability["department"],
                "adaptation_notes": recommendation["adaptation_notes"],
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


def write_department_shopping_state(
    project_dir: Path,
    department_shopping: dict[str, dict[str, Any]],
) -> None:
    state_dir = project_dir / ".brain" / "state" / "departments"
    state_dir.mkdir(parents=True, exist_ok=True)
    for department, payload in department_shopping.items():
        path = state_dir / f"{department}-shopping.json"
        path.write_text(json.dumps(payload, indent=2) + "\n")


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
    all_departments = sorted(set(departments) | {item["department"] for item in capabilities})
    source_packs = load_department_source_packs(project_dir, all_departments)
    (
        local_skills,
        global_skills,
        external_skills,
        radar_skills,
        project_tips,
        catalog_versions,
        external_generated_at,
    ) = load_local_global_external_skills(
        project_dir,
        claude_home,
        approved_external_roots,
    )

    active, stale = classify_local_skills(capabilities, local_skills)
    active_titles = {item["title"] for item in active}
    recommendations: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    capabilities_by_title = {item["title"]: item for item in capabilities}
    department_shopping = {
        department: {
            "department": department,
            "reviewed_at": now_utc(),
            "last_refresh": now_utc(),
            "missing_capabilities": [],
            "candidate_skills": [],
            "adopted_skills": [],
            "rejected_candidates": [],
            "source_pack": source_packs.get(department, {}),
            "source_catalog_version": 0,
            "next_review_at": None,
        }
        for department in all_departments
    }

    global_external = global_skills + radar_skills + external_skills
    for capability in capabilities:
        department = capability["department"]
        if capability["title"] in {cap for item in active for cap in item["matched_capabilities"]}:
            continue
        match = match_capability(
            capability,
            global_external,
            source_pack=source_packs.get(department, {}),
            exclude_slugs={slugify(title) for title in active_titles},
            project_tips=project_tips,
        )
        if match and match["score"] >= 2:
            recommendations.append(match)
            if department in department_shopping:
                department_shopping[department]["candidate_skills"].append(match)
            continue
        missing_item = {
            "title": capability["title"],
            "department": department,
            "reason": capability["reason"],
        }
        missing.append(missing_item)
        if department in department_shopping:
            department_shopping[department]["missing_capabilities"].append(missing_item)

    materialized = materialize_recommendations(
        project_dir,
        recommendations,
        capabilities_by_title,
        source_packs=source_packs,
    )
    if materialized:
        local_skills, _, _, _, _, _, _ = load_local_global_external_skills(
            project_dir,
            claude_home,
            approved_external_roots,
        )
        active, stale = classify_local_skills(capabilities, local_skills)
        materialized_titles = {item["title"] for item in materialized}
        recommendations = [
            item for item in recommendations if item["title"] not in materialized_titles
        ]
        for item in materialized:
            department_shopping[item["department"]]["adopted_skills"].append(item)

    for department, payload in department_shopping.items():
        payload["source_catalog_version"] = int(catalog_versions.get("skill_catalog", 0))
        payload["candidate_skills"] = sorted(
            payload["candidate_skills"],
            key=lambda item: (item["score"], item["source_trust"], -item["freshness_days"]),
            reverse=True,
        )[:5]

    payload = {
        "generated_at": now_utc(),
        "repo": project_dir.name,
        "departments": all_departments,
        "last_external_refresh": external_generated_at,
        "catalog_versions": catalog_versions,
        "required_capabilities": capabilities,
        "active": active,
        "recommended": [
            {
                "title": item["title"],
                "capability": item["capability"],
                "source": item["source"],
                "score": item["score"],
                "source_path": item["source_path"],
                "department": item["department"],
                "source_trust": item["source_trust"],
                "freshness_days": item["freshness_days"],
                "match_reasons": item["match_reasons"],
                "adaptation_notes": item["adaptation_notes"],
            }
            for item in recommendations
        ],
        "materialized": materialized,
        "stale": stale,
        "missing": missing,
        "department_shopping": department_shopping,
        "inventory_counts": {
            "repo": len(local_skills),
            "global": len(global_skills),
            "radar": len(radar_skills),
            "external": len(external_skills),
        },
    }
    write_department_shopping_state(project_dir, department_shopping)
    write_skill_state(project_dir, payload)
    return payload
