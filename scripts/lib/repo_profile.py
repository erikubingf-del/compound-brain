from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any


ROOT_CONTEXT_FILES = [
    "README.md",
    "CLAUDE.md",
    "ARCHITECTURE.md",
    "package.json",
    "pyproject.toml",
    "go.mod",
    "Cargo.toml",
]

DOC_GLOBS = [
    "docs/**/*.md",
    "docs/**/*.json",
    "docs/**/*.txt",
]

DOMAIN_KEYWORDS: list[tuple[str, list[str]]] = [
    (
        "crm",
        [
            "crm",
            "customer relationship",
            "lead",
            "leads",
            "deal",
            "deals",
            "pipeline",
            "contact",
            "contacts",
            "account management",
            "sales",
        ],
    ),
    (
        "trading",
        [
            "trading system",
            "backtest",
            "portfolio",
            "execution",
            "market structure",
            "risk",
            "alpha",
            "strategy",
            "broker",
            "order book",
        ],
    ),
]


def safe_read_text(path: Path, limit: int = 6000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return text[:limit]


def parse_package_metadata(repo_root: Path) -> dict[str, Any]:
    package_path = repo_root / "package.json"
    if not package_path.exists():
        return {}
    try:
        payload = json.loads(package_path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return {
        "name": payload.get("name", ""),
        "description": payload.get("description", ""),
        "keywords": payload.get("keywords", []),
        "scripts": sorted(list((payload.get("scripts") or {}).keys())),
    }


def collect_context_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()

    for name in ROOT_CONTEXT_FILES:
        path = repo_root / name
        if path.exists() and path not in seen:
            files.append(path)
            seen.add(path)

    for pattern in DOC_GLOBS:
        for path in sorted(repo_root.glob(pattern))[:20]:
            if path.is_file() and path not in seen:
                files.append(path)
                seen.add(path)

    return files


def collect_repo_context(repo_root: Path) -> dict[str, Any]:
    files = collect_context_files(repo_root)
    parts: list[str] = []
    for path in files:
        relative = path.relative_to(repo_root)
        parts.append(f"[file:{relative}]")
        parts.append(safe_read_text(path))

    package_metadata = parse_package_metadata(repo_root)
    if package_metadata:
        parts.append("[package-metadata]")
        parts.append(json.dumps(package_metadata, indent=2))

    return {
        "files": [str(path.relative_to(repo_root)) for path in files],
        "text": "\n".join(parts).lower(),
        "package_metadata": package_metadata,
    }


def infer_repo_native_departments(context_text: str) -> list[str]:
    matches = re.findall(r"\bd\d{2}\b", context_text)
    ordered: list[str] = []
    for item in matches:
        upper = item.upper()
        if upper not in ordered:
            ordered.append(upper)
    return ordered


def infer_project_goal(repo_name: str, context_text: str, fallback: str) -> str:
    best_domain = ""
    best_score = 0
    for domain, keywords in DOMAIN_KEYWORDS:
        score = sum(context_text.count(keyword) for keyword in keywords)
        if score > best_score:
            best_domain = domain
            best_score = score

    if best_domain == "crm" and best_score >= 2:
        return (
            f"Operate {repo_name} as a CRM system that improves lead, contact, "
            "and pipeline workflows with durable project memory and bounded autonomy."
        )
    if best_domain == "trading" and best_score >= 2:
        return (
            f"Operate {repo_name} as a trading system that improves strategy quality, "
            "execution safety, and risk-aware iteration through evaluator-backed decisions."
        )
    return fallback


def existing_relative_paths(repo_root: Path, candidates: list[str]) -> list[str]:
    resolved: list[str] = []
    for candidate in candidates:
        path = repo_root / candidate
        if path.exists():
            resolved.append(str(path.relative_to(repo_root)))
    return resolved


def generic_surface_candidates(repo_root: Path) -> list[str]:
    candidates = [
        "README.md",
        "docs",
        "src",
        "app",
        "lib",
        "tests",
        "package.json",
        "pyproject.toml",
    ]
    resolved = existing_relative_paths(repo_root, candidates)
    return resolved[:4]


def build_department_surfaces(repo_root: Path, departments: list[str]) -> dict[str, list[str]]:
    surface_map: dict[str, list[str]] = {}
    default_map = {
        "architecture": [
            "ARCHITECTURE.md",
            "CLAUDE.md",
            "README.md",
            "docs",
            "scripts",
            "orchestrators",
        ],
        "engineering": [
            "src",
            "app",
            "lib",
            "server",
            "api",
            "components",
            "pages",
            "tests",
            "package.json",
            "pyproject.toml",
        ],
        "operations": [
            ".github/workflows",
            "Dockerfile",
            "docker-compose.yml",
            "infra",
            "deploy",
            "ops",
            "Procfile",
            "vercel.json",
            "railway.json",
            "fly.toml",
            "terraform",
            "k8s",
        ],
        "product": [
            "README.md",
            "docs",
            "docs/crm-v2",
            "content",
            "public",
            "package.json",
        ],
        "research": [
            "research",
            "experiments",
            "notebooks",
            "docs/research",
        ],
    }

    all_existing = [
        str(path.relative_to(repo_root))
        for path in sorted(repo_root.rglob("*"))
        if path.is_file() and ".git" not in path.parts
    ]
    lower_lookup = {path.lower(): path for path in all_existing}

    for department in departments:
        if department in default_map:
            surfaces = existing_relative_paths(repo_root, default_map[department])
        elif re.fullmatch(r"D\d{2}", department):
            token = department.lower()
            surfaces = [path for path in all_existing if token in path.lower()][:6]
        else:
            surfaces = []

        if not surfaces:
            surfaces = generic_surface_candidates(repo_root)
        if not surfaces and "readme.md" in lower_lookup:
            surfaces = [lower_lookup["readme.md"]]
        surface_map[department] = surfaces
    return surface_map


def augment_departments(
    default_departments: list[str],
    repo_root: Path,
    tech_stack: list[str],
    docs_present: bool,
    ci_present: bool,
) -> list[str]:
    departments = list(default_departments)
    surfaces = build_department_surfaces(repo_root, ["operations", "product", "research"])
    if surfaces.get("operations") and "operations" not in departments:
        departments.append("operations")
    if (docs_present or surfaces.get("product")) and "product" not in departments:
        departments.append("product")
    if (surfaces.get("research") or any(tech in tech_stack for tech in ["Python", "TypeScript", "JavaScript"])) and "research" not in departments:
        departments.append("research")
    return departments


def build_repo_profile(
    repo_root: Path,
    repo_name: str,
    tech_stack: list[str],
    docs_present: bool,
    ci_present: bool,
    default_departments: list[str],
    fallback_goal: str,
) -> dict[str, Any]:
    context = collect_repo_context(repo_root)
    departments = augment_departments(default_departments, repo_root, tech_stack, docs_present, ci_present)
    project_goal = infer_project_goal(repo_name, context["text"], fallback_goal)
    native_departments = infer_repo_native_departments(context["text"])
    return {
        "context_files": context["files"],
        "package_metadata": context["package_metadata"],
        "project_goal": project_goal,
        "departments": departments,
        "repo_native_departments": native_departments,
        "department_surfaces": build_department_surfaces(repo_root, departments),
    }


def write_repo_profile(repo_root: Path, payload: dict[str, Any]) -> None:
    state_path = repo_root / ".brain" / "state" / "repo-profile.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2) + "\n")
