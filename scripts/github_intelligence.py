#!/usr/bin/env python3
"""
github_intelligence.py — Weekly external intelligence sweep from GitHub.

For each registered project, searches GitHub for:
- Similar projects / competitors
- New patterns, libraries, or approaches in the domain
- Trending repos in the project's tech stack
- Architectural inspiration

Writes findings to:
- ~/.claude/knowledge/resources/github-intel-YYYY-MM-DD.md (global)
- <project>/.brain/knowledge/resources/github-intel.md (per-project)

Uses GitHub API (no auth required for public search, rate-limited to 10 req/min).
Optionally uses web search MCP if available.

Usage:
    python3 github_intelligence.py
    python3 github_intelligence.py --project-dir /path/to/project  # single project
    python3 github_intelligence.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.architecture_radar import finding_from_repo, rank_findings, render_radar
except ModuleNotFoundError:
    from architecture_radar import finding_from_repo, rank_findings, render_radar

CLAUDE_BIN = "__CLAUDE_BIN__"
CONFIG_FILE = Path.home() / ".claude" / "intelligence_projects.json"
GLOBAL_KNOWLEDGE = Path.home() / ".claude" / "knowledge"
GITHUB_API = "https://api.github.com/search/repositories"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def date_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def read_safe(path: Path, max_chars: int = 2000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""


# ─── GitHub API ──────────────────────────────────────────────────────────────

def github_search(query: str, sort: str = "stars", per_page: int = 5) -> list[dict]:
    """Search GitHub repos. Returns list of repo dicts."""
    params = urllib.parse.urlencode({
        "q": query,
        "sort": sort,
        "order": "desc",
        "per_page": per_page,
    })
    url = f"{GITHUB_API}?{params}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "compound-brain/1.0",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("items", [])
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  [github] Rate limited — sleeping 60s")
            time.sleep(60)
            return []
        return []
    except Exception as e:
        print(f"  [github] Search failed: {e}")
        return []


def format_repo(repo: dict) -> str:
    return (
        f"**[{repo.get('full_name', '?')}]({repo.get('html_url', '')})**  "
        f"⭐{repo.get('stargazers_count', 0):,} | "
        f"{repo.get('description', 'No description')[:100]}"
    )


# ─── Per-project intel ───────────────────────────────────────────────────────

def get_project_search_terms(project_dir: Path) -> list[str]:
    """Extract domain-relevant search terms from project."""
    terms = []

    # From CLAUDE.md
    claude_md = read_safe(project_dir / "CLAUDE.md", 1500)
    # From README
    readme = read_safe(project_dir / "README.md", 1000)
    combined = (claude_md + " " + readme).lower()

    # Tech stack detection
    if "trading" in combined or "polymarket" in combined or "binance" in combined:
        terms.extend(["algorithmic trading python", "prediction market bot", "crypto trading strategy"])
    if "whatsapp" in combined:
        terms.extend(["whatsapp bot automation", "whatsapp web nodejs"])
    if "saas" in combined or "subscription" in combined:
        terms.extend(["saas boilerplate nextjs", "subscription billing stripe"])
    if "ai agent" in combined or "llm" in combined or "langchain" in combined:
        terms.extend(["ai agent framework", "llm autonomous agent python"])
    if "react" in combined or "nextjs" in combined:
        terms.extend(["nextjs saas template", "react dashboard template"])

    # Always search for "autonomous llm second brain" regardless
    terms.append("llm second brain knowledge management")
    terms.append("claude code hooks automation")

    return list(dict.fromkeys(terms))[:5]  # deduplicate, limit to 5


def run_github_intel_for_project(project_dir: Path) -> tuple[str, list[dict]]:
    """Search GitHub for project-relevant repos. Returns markdown findings and radar candidates."""
    name = project_dir.name
    print(f"  [{name}] Getting search terms...")
    terms = get_project_search_terms(project_dir)

    findings: list[str] = []
    radar_candidates: list[dict] = []
    findings.append(f"# GitHub Intelligence — {name}\n*Sweep: {now_utc()}*\n")

    for term in terms:
        print(f"  [{name}] Searching: {term}")
        repos = github_search(term, sort="stars", per_page=3)
        if repos:
            findings.append(f"\n## Search: `{term}`\n")
            for repo in repos:
                findings.append(f"- {format_repo(repo)}")
                radar_candidates.append(finding_from_repo(term, repo))
        time.sleep(6)  # Respect GitHub rate limit (10 req/min)

    return "\n".join(findings), rank_findings(radar_candidates)


# ─── LLM synthesis ───────────────────────────────────────────────────────────

def synthesize_with_llm(project_dir: Path, raw_findings: str) -> str:
    """Ask Claude to synthesize GitHub findings into actionable insights."""
    project_name = project_dir.name
    project_context = read_safe(project_dir / "CLAUDE.md", 800)

    prompt = f"""You are the compound-brain GitHub intelligence analyst for project "{project_name}".

Project context:
{project_context[:500]}

GitHub search results:
{raw_findings[:2000]}

Synthesize these findings into actionable intelligence:

1. **Most Relevant Discovery** (1-2 sentences): Which repo is most worth examining and why?
2. **Architectural Pattern to Consider** (2-3 bullets): What patterns in these repos could improve this project?
3. **Technology Gap** (1 bullet): Is there a library or approach in these repos that this project should evaluate?
4. **Competitive Awareness** (1 bullet): Any direct competitors or close alternatives found?
5. **Recommended Action** (1 sentence): Specific thing to investigate or adopt.

Max 150 words. Be concrete — reference actual repos found."""

    try:
        result = subprocess.run(
            [CLAUDE_BIN, "--dangerously-skip-permissions", "--print", "-p", prompt],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "LLM synthesis unavailable — see raw findings above."


# ─── Output ──────────────────────────────────────────────────────────────────

def write_project_intel(project_dir: Path, raw: str, synthesis: str, ranked_findings: list[dict]) -> None:
    brain_res = project_dir / ".brain" / "knowledge" / "resources"
    brain_res.mkdir(parents=True, exist_ok=True)

    path = brain_res / "github-intel.md"
    content = f"{raw}\n\n## AI Synthesis\n{synthesis}\n"
    path.write_text(content)
    print(f"  Written → {path}")

    radar_path = brain_res / "architecture-radar.md"
    radar_path.write_text(
        render_radar(f"Architecture Radar — {project_dir.name}", ranked_findings[:5])
    )
    print(f"  Written → {radar_path}")


def write_global_summary(all_synthesis: dict[str, str], all_findings: list[dict]) -> None:
    d = date_str()
    ts = now_utc()
    daily = GLOBAL_KNOWLEDGE / "daily"
    daily.mkdir(parents=True, exist_ok=True)
    resources = GLOBAL_KNOWLEDGE / "resources"
    resources.mkdir(parents=True, exist_ok=True)

    report_path = resources / f"github-intel-{d}.md"
    latest_path = resources / "github-intel-latest.md"

    lines = [f"# GitHub Intelligence Sweep — {ts}\n"]
    for project_name, synthesis in all_synthesis.items():
        lines.append(f"\n## {project_name}\n{synthesis}")

    content = "\n".join(lines)
    report_path.write_text(content)
    latest_path.write_text(content)
    print(f"\n[github-intel] Global report → {report_path}")

    ranked = rank_findings(all_findings)
    radar_report_path = resources / f"architecture-radar-{d}.md"
    radar_latest_path = resources / "architecture-radar.md"
    radar_content = render_radar(f"Global Architecture Radar — {ts}", ranked[:10])
    radar_report_path.write_text(radar_content)
    radar_latest_path.write_text(radar_content)
    print(f"[github-intel] Architecture radar → {radar_latest_path}")


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="GitHub intelligence sweep for compound-brain")
    parser.add_argument("--project-dir", help="Single project path (default: all registered)")
    parser.add_argument("--dry-run", action="store_true", help="Show search terms without calling GitHub")
    args = parser.parse_args()

    print(f"[github-intel] Starting sweep {now_utc()}")

    if args.project_dir:
        project_dirs = [Path(args.project_dir).resolve()]
    else:
        config = json.loads(CONFIG_FILE.read_text()) if CONFIG_FILE.exists() else {}
        project_dirs = [Path(p["path"]) for p in config.get("projects", []) if p.get("enabled", True)]

    if not project_dirs:
        print("[github-intel] No projects registered. Add with: python3 global_intelligence_sweeper.py --register /path")
        return

    all_synthesis: dict[str, str] = {}
    all_findings: list[dict] = []

    for project_dir in project_dirs:
        if not project_dir.exists():
            continue

        if args.dry_run:
            terms = get_project_search_terms(project_dir)
            print(f"\n[{project_dir.name}] Would search:")
            for t in terms:
                print(f"  - {t}")
            continue

        print(f"\n[github-intel] → {project_dir.name}")
        raw, ranked_findings = run_github_intel_for_project(project_dir)
        synthesis = synthesize_with_llm(project_dir, raw)
        write_project_intel(project_dir, raw, synthesis, ranked_findings)
        all_synthesis[project_dir.name] = synthesis
        all_findings.extend(ranked_findings)

    if all_synthesis:
        write_global_summary(all_synthesis, all_findings)

    print(f"\n[github-intel] Done. {now_utc()}")


if __name__ == "__main__":
    main()
