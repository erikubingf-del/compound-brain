from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from typing import Any, Callable

try:
    from scripts.github_intelligence import github_search as github_search_api
    from scripts.lib.skill_inventory import (
        enabled_departments,
        infer_required_capabilities,
        load_department_source_packs,
        normalize_tokens,
        slugify,
    )
except ModuleNotFoundError:
    from github_intelligence import github_search as github_search_api
    from lib.skill_inventory import (
        enabled_departments,
        infer_required_capabilities,
        load_department_source_packs,
        normalize_tokens,
        slugify,
    )


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def claude_home_dir() -> Path:
    override = os.environ.get("COMPOUND_BRAIN_HOME")
    if override:
        return Path(override)
    return Path.home() / ".claude"


def resources_dir(claude_home: Path) -> Path:
    return claude_home / "knowledge" / "resources"


def registry_path(claude_home: Path) -> Path:
    return claude_home / "registry" / "activated-projects.json"


def load_skill_radar_policy(claude_home: Path) -> dict[str, Any]:
    path = claude_home / "policy" / "skill-radar-policy.json"
    if path.exists():
        return json.loads(path.read_text())
    return {
        "version": 1,
        "refresh_hours": 12,
        "per_query_limit": 3,
        "max_queries_per_repo": 6,
        "max_candidates_per_repo": 12,
        "minimum_stars": 300,
        "minimum_stars_by_department": {
            "architecture": 750,
            "engineering": 500,
            "operations": 500,
            "product": 250,
            "research": 400,
        },
        "approved_query_terms": [],
    }


def load_project_dirs(claude_home: Path) -> list[Path]:
    path = registry_path(claude_home)
    if not path.exists():
        return []
    payload = json.loads(path.read_text())
    projects = []
    for item in payload.get("projects", []):
        repo_path = item.get("repo_path")
        if repo_path:
            project_dir = Path(repo_path).expanduser().resolve()
            if project_dir.exists():
                projects.append(project_dir)
    return projects


def parse_iso8601(value: str) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def freshness_days(updated_at: str) -> int:
    parsed = parse_iso8601(updated_at)
    if parsed is None:
        return 9999
    return max(int((datetime.now(timezone.utc) - parsed).total_seconds() // 86400), 0)


def source_pack_queries(source_pack: dict[str, Any]) -> list[str]:
    return [str(item).strip() for item in source_pack.get("search_queries", []) if str(item).strip()]


def operator_rationale(repo: Path) -> list[str]:
    path = repo / ".brain" / "state" / "operator-recommendation.json"
    if not path.exists():
        return []
    payload = json.loads(path.read_text())
    return [str(item) for item in payload.get("rationale", []) if str(item).strip()]


def build_repo_queries(repo: Path, policy: dict[str, Any]) -> list[dict[str, str]]:
    departments = enabled_departments(repo)
    capabilities = infer_required_capabilities(repo, departments)
    source_packs = load_department_source_packs(repo, departments)
    rationale = operator_rationale(repo)
    queries: list[dict[str, str]] = []

    for capability in capabilities:
        department = capability["department"]
        capability_name = capability["title"]
        source_pack = source_packs.get(department, {})
        base_query = f"{capability_name} {department} github"
        queries.append(
            {
                "department": department,
                "capability": capability_name,
                "query": base_query,
            }
        )
        for query in source_pack_queries(source_pack)[:2]:
            queries.append(
                {
                    "department": department,
                    "capability": capability_name,
                    "query": f"{query} github",
                }
            )

    for hint in rationale[:2]:
        queries.append(
            {
                "department": departments[0] if departments else "architecture",
                "capability": "Operator Guidance",
                "query": f"{hint} github",
            }
        )

    seen: set[str] = set()
    filtered: list[dict[str, str]] = []
    approved_terms = {item.lower() for item in policy.get("approved_query_terms", [])}
    for query in queries:
        q = " ".join(query["query"].split())
        key = q.lower()
        if key in seen:
            continue
        if approved_terms:
            tokens = normalize_tokens(q)
            if not (tokens & approved_terms):
                continue
        seen.add(key)
        filtered.append({**query, "query": q})
        if len(filtered) >= int(policy.get("max_queries_per_repo", 6)):
            break
    return filtered


def github_search(query: str, per_page: int = 3) -> list[dict[str, Any]]:
    return github_search_api(query, sort="stars", per_page=per_page)


def call_github_search(
    github_search_fn: Callable[..., list[dict[str, Any]]],
    query: str,
    per_page: int,
) -> list[dict[str, Any]]:
    try:
        return github_search_fn(query, per_page=per_page)
    except TypeError:
        return github_search_fn(query, sort="stars", per_page=per_page)


def candidate_from_repo(
    repo: Path,
    query_record: dict[str, str],
    found_repo: dict[str, Any],
) -> dict[str, Any]:
    title = found_repo.get("full_name") or found_repo.get("name") or "unknown"
    summary = str(found_repo.get("description") or "No description provided.")
    stars = int(found_repo.get("stargazers_count", 0))
    updated_at = str(found_repo.get("updated_at") or "")
    fresh_days = freshness_days(updated_at)
    query = query_record["query"]
    capability = query_record["capability"]
    department = query_record["department"]
    tokens = normalize_tokens(title, summary, query, capability, department)
    goal_overlap = len(tokens & normalize_tokens(repo.name, capability, department))
    goal_fit = min(0.98, 0.45 + (goal_overlap * 0.08) + min(stars / 10000, 0.25))
    source_trust = min(0.98, 0.45 + min(stars / 10000, 0.45) + (0.08 if fresh_days <= 30 else 0))
    confidence = min(0.97, 0.4 + (goal_fit * 0.35) + (source_trust * 0.25))
    return {
        "id": slugify(f"{title}-{capability}"),
        "title": title.split("/")[-1],
        "kind": "external-skill",
        "source_type": "github",
        "source_name": title,
        "source_url": found_repo.get("html_url", ""),
        "stars": stars,
        "updated_at": updated_at,
        "language_hints": [str(found_repo.get("language") or "").lower()] if found_repo.get("language") else [],
        "department_hints": [department],
        "capability_hints": [slugify(capability)],
        "summary": summary,
        "candidate_tip": f"Adapt {capability.lower()} patterns from {title}.",
        "source_trust": round(source_trust, 2),
        "freshness_days": fresh_days,
        "goal_fit": round(goal_fit, 2),
        "confidence": round(confidence, 2),
        "search_query": query,
        "repo_name": repo.name,
    }


def bullet_lines(path: Path, heading_prefix: str = "## ") -> list[str]:
    if not path.exists():
        return []
    lines: list[str] = []
    capture = False
    for raw_line in path.read_text().splitlines():
        stripped = raw_line.strip()
        if stripped.startswith(heading_prefix):
            capture = True
            continue
        if capture and stripped.startswith("#"):
            break
        if stripped.startswith("- "):
            lines.append(stripped[2:].strip())
    return lines


def extract_project_tips(repo: Path) -> list[dict[str, Any]]:
    tips: list[dict[str, Any]] = []
    operator_path = repo / ".brain" / "state" / "operator-recommendation.json"
    if operator_path.exists():
        payload = json.loads(operator_path.read_text())
        department = str(payload.get("lead_department") or "architecture")
        rationale = [str(item) for item in payload.get("rationale", []) if str(item).strip()]
        if rationale:
            tips.append(
                {
                    "id": slugify(f"{repo.name}-{department}-operator-tip"),
                    "source_repo": repo.name,
                    "department": department,
                    "capability": slugify(" ".join(payload.get("missing_skills", [])[:1]) or department),
                    "tip": rationale[0],
                    "evidence_count": max(1, len(rationale)),
                    "success_count": 1,
                    "failure_count": 0,
                    "last_seen": now_utc(),
                    "promotion_level": "repo-skill-candidate",
                    "confidence": 0.72,
                }
            )

    for memory_file in sorted((repo / ".brain" / "knowledge" / "departments").glob("*.md")):
        lessons = bullet_lines(memory_file)
        if not lessons:
            continue
        department = memory_file.stem.replace("-sources", "")
        tips.append(
            {
                "id": slugify(f"{repo.name}-{department}-memory-tip"),
                "source_repo": repo.name,
                "department": department,
                "capability": slugify(department),
                "tip": lessons[0],
                "evidence_count": min(len(lessons), 4),
                "success_count": 1,
                "failure_count": 0,
                "last_seen": now_utc(),
                "promotion_level": "local-tip",
                "confidence": 0.68,
            }
        )

    results_path = repo / ".brain" / "autoresearch" / "results.jsonl"
    if results_path.exists():
        for line in reversed(results_path.read_text().splitlines()):
            if not line.strip():
                continue
            payload = json.loads(line)
            if payload.get("status") not in {"kept", "baseline-recorded"}:
                continue
            hypothesis = str(payload.get("hypothesis") or payload.get("notes") or "").strip()
            if not hypothesis:
                continue
            department = str(payload.get("department") or "research")
            tips.append(
                {
                    "id": slugify(f"{repo.name}-{department}-autoresearch-tip"),
                    "source_repo": repo.name,
                    "department": department,
                    "capability": slugify(department),
                    "tip": hypothesis,
                    "evidence_count": 2,
                    "success_count": 1,
                    "failure_count": 0,
                    "last_seen": now_utc(),
                    "promotion_level": "global-candidate",
                    "confidence": 0.8,
                }
            )
            break

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for tip in tips:
        if tip["id"] in seen:
            continue
        seen.add(tip["id"])
        deduped.append(tip)
    return deduped


def write_markdown_summary(
    resources: Path,
    skill_catalog: dict[str, Any],
    project_tip_catalog: dict[str, Any],
) -> None:
    latest_path = resources / "skill-radar-latest.md"
    history_dir = resources / "skill-radar-history"
    history_dir.mkdir(parents=True, exist_ok=True)
    date_slug = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    history_path = history_dir / f"{date_slug}.md"

    lines = [
        "# Skill Radar",
        "",
        f"Generated: {skill_catalog['generated_at']}",
        "",
        "## External Candidates",
    ]
    for candidate in skill_catalog.get("candidates", [])[:10]:
        lines.append(
            "- "
            + f"**{candidate['title']}** from `{candidate['source_name']}` "
            + f"(⭐{candidate['stars']}, dept={candidate['department_hints'][0]}, "
            + f"capability={candidate['capability_hints'][0]})"
        )
    if not skill_catalog.get("candidates"):
        lines.append("- none")

    lines.extend(["", "## Project Tips"])
    for tip in project_tip_catalog.get("tips", [])[:10]:
        lines.append(
            "- "
            + f"`{tip['source_repo']}` / `{tip['department']}`: {tip['tip']}"
        )
    if not project_tip_catalog.get("tips"):
        lines.append("- none")

    content = "\n".join(lines) + "\n"
    latest_path.write_text(content)
    history_path.write_text(content)


def refresh_skill_radar(
    *,
    claude_home: Path | None = None,
    project_dirs: list[Path] | None = None,
    github_search_fn: Callable[..., list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    claude_home = (claude_home or claude_home_dir()).resolve()
    project_dirs = [path.resolve() for path in (project_dirs or load_project_dirs(claude_home))]
    github_search_fn = github_search_fn or github_search
    policy = load_skill_radar_policy(claude_home)
    resources = resources_dir(claude_home)
    resources.mkdir(parents=True, exist_ok=True)

    per_query_limit = int(policy.get("per_query_limit", 3))
    minimum_stars = int(policy.get("minimum_stars", 300))
    minimum_by_department = {
        str(key): int(value)
        for key, value in dict(policy.get("minimum_stars_by_department", {})).items()
    }

    candidates: list[dict[str, Any]] = []
    all_tips: list[dict[str, Any]] = []
    sources_scanned = 0

    for repo in project_dirs:
        queries = build_repo_queries(repo, policy)
        for query_record in queries:
            department = query_record["department"]
            stars_floor = minimum_by_department.get(department, minimum_stars)
            for found_repo in call_github_search(github_search_fn, query_record["query"], per_query_limit):
                stars = int(found_repo.get("stargazers_count", 0))
                if stars < stars_floor:
                    continue
                candidates.append(candidate_from_repo(repo, query_record, found_repo))
                sources_scanned += 1
                if len([item for item in candidates if item["repo_name"] == repo.name]) >= int(
                    policy.get("max_candidates_per_repo", 12)
                ):
                    break
        all_tips.extend(extract_project_tips(repo))

    deduped_candidates: list[dict[str, Any]] = []
    seen_candidates: set[str] = set()
    for candidate in sorted(
        candidates,
        key=lambda item: (
            float(item.get("confidence", 0)),
            float(item.get("source_trust", 0)),
            int(item.get("stars", 0)),
        ),
        reverse=True,
    ):
        key = f"{candidate['source_name']}::{candidate['capability_hints'][0]}::{candidate['repo_name']}"
        if key in seen_candidates:
            continue
        seen_candidates.add(key)
        deduped_candidates.append(candidate)

    deduped_tips: list[dict[str, Any]] = []
    seen_tips: set[str] = set()
    for tip in all_tips:
        if tip["id"] in seen_tips:
            continue
        seen_tips.add(tip["id"])
        deduped_tips.append(tip)

    generated_at = now_utc()
    next_refresh_due = (
        datetime.now(timezone.utc) + timedelta(hours=int(policy.get("refresh_hours", 12)))
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    skill_catalog = {
        "version": 1,
        "generated_at": generated_at,
        "next_refresh_due": next_refresh_due,
        "sources_scanned": sources_scanned,
        "candidates": deduped_candidates,
    }
    project_tip_catalog = {
        "version": 1,
        "generated_at": generated_at,
        "repos_seen": len(project_dirs),
        "tips": deduped_tips,
    }

    (resources / "skill-catalog.json").write_text(json.dumps(skill_catalog, indent=2) + "\n")
    (resources / "project-tip-catalog.json").write_text(json.dumps(project_tip_catalog, indent=2) + "\n")
    write_markdown_summary(resources, skill_catalog, project_tip_catalog)
    return {
        "skill_catalog": skill_catalog,
        "project_tip_catalog": project_tip_catalog,
    }
