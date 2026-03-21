#!/usr/bin/env python3
"""
probability_engine.py — Direction scoring for compound-brain agents.

Scores candidate actions by Expected Value:
  EV = (Impact × P_success × Urgency) / Cost

Agents call rank_actions() before choosing next steps.
The reasoning is logged so outcomes can validate and improve the model.

Usage (as library):
    from probability_engine import rank_actions, ProjectState, Action
    state = ProjectState.from_brain(project_dir)
    actions = rank_actions(state, candidates)
    best = actions[0]

Usage (CLI — generate action candidates and rank them):
    python3 probability_engine.py --project-dir /path/to/project
    python3 probability_engine.py --project-dir /path/to/project --output json
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

CLAUDE_BIN = "__CLAUDE_BIN__"
STAGE_LABELS = {
    (0, 2): "bootstrap",      # First commits, no tests, no docs
    (2, 4): "foundation",     # Core logic exists, rough edges
    (4, 6): "growth",         # Working product, adding features
    (6, 8): "optimization",   # Stable, improving performance/reliability
    (8, 10): "maintenance",   # Mature, incremental updates
}

ActionCategory = Literal["feature", "fix", "debt", "docs", "infra", "research", "security", "test"]


@dataclass
class ProjectState:
    """Snapshot of a project's current state for probability scoring."""

    project_dir: Path
    project_name: str
    stage: float                    # 0-10 maturity score
    goal: str                       # project's stated objective
    recent_commits: list[str]       # last 10 commit messages
    open_issues: list[str]          # known issues/blockers
    test_pass_rate: float           # 0-1 (1.0 = all passing)
    days_since_last_commit: int
    has_brain: bool
    has_planning: bool
    brain_decisions: list[str]      # recent decision log entries
    skills: list[str]               # active skills/capabilities
    notes: str = ""                 # free-form context

    @classmethod
    def from_brain(cls, project_dir: Path) -> "ProjectState":
        """Construct ProjectState by reading .brain/ and git history."""
        project_dir = Path(project_dir).resolve()
        name = project_dir.name

        # Git activity
        commits = _git_log(project_dir)
        days_since = _days_since_last_commit(project_dir)

        # Project goal from CLAUDE.md or brain
        goal = _read_project_goal(project_dir)

        # Brain state
        has_brain = (project_dir / ".brain").exists()
        has_planning = (project_dir / ".planning").exists()
        decisions = _read_brain_decisions(project_dir)
        skills = _read_brain_skills(project_dir)
        issues = _detect_open_issues(project_dir)

        # Stage estimation
        stage = _estimate_stage(project_dir, commits, days_since, has_brain, has_planning)

        return cls(
            project_dir=project_dir,
            project_name=name,
            stage=stage,
            goal=goal,
            recent_commits=commits,
            open_issues=issues,
            test_pass_rate=_estimate_test_health(project_dir),
            days_since_last_commit=days_since,
            has_brain=has_brain,
            has_planning=has_planning,
            brain_decisions=decisions,
            skills=skills,
        )

    def stage_label(self) -> str:
        for (lo, hi), label in STAGE_LABELS.items():
            if lo <= self.stage < hi:
                return label
        return "unknown"


@dataclass
class Action:
    """A candidate action for the project."""

    title: str
    category: ActionCategory
    description: str
    expected_impact: float      # 0-10: how much does this move toward goal?
    p_success: float            # 0-1: probability this works given current state
    urgency: float              # 0-10: how bad if delayed?
    cost: float                 # 1-10: complexity/risk (higher = more costly)
    reasoning: str = ""
    ev: float = 0.0             # computed by rank_actions()

    def compute_ev(self) -> float:
        """EV = (impact × p_success × urgency) / cost"""
        self.ev = (self.expected_impact * self.p_success * self.urgency) / max(self.cost, 0.1)
        return self.ev


@dataclass
class RankingResult:
    """Output from rank_actions()."""

    timestamp: str
    project: str
    stage: str
    goal: str
    ranked: list[Action]
    top_action: Action
    reasoning: str


def rank_actions(state: ProjectState, candidates: list[Action] | None = None) -> RankingResult:
    """
    Score and rank actions for a project.

    If candidates is None, generates them via LLM call.
    Returns ranked list with EV scores and reasoning.
    """
    if candidates is None:
        candidates = _generate_candidates_via_llm(state)

    # Score each candidate
    for action in candidates:
        action.compute_ev()

    # Sort by EV descending
    ranked = sorted(candidates, key=lambda a: a.ev, reverse=True)

    # Build reasoning narrative
    reasoning = _build_reasoning(state, ranked[:3])

    # Log to brain
    _log_ranking(state.project_dir, ranked[:5], reasoning)

    return RankingResult(
        timestamp=datetime.now(timezone.utc).isoformat(),
        project=state.project_name,
        stage=state.stage_label(),
        goal=state.goal,
        ranked=ranked,
        top_action=ranked[0] if ranked else Action("no-op", "docs", "Nothing to do", 0, 1, 0, 1),
        reasoning=reasoning,
    )


# ─── LLM candidate generation ────────────────────────────────────────────────

def _generate_candidates_via_llm(state: ProjectState) -> list[Action]:
    """Ask Claude to generate ranked action candidates given project state."""
    prompt = f"""You are the probability engine for project "{state.project_name}".

Project state:
- Stage: {state.stage}/10 ({state.stage_label()})
- Goal: {state.goal}
- Days since last commit: {state.days_since_last_commit}
- Recent commits: {', '.join(state.recent_commits[:5])}
- Open issues: {', '.join(state.open_issues[:5]) if state.open_issues else 'none known'}
- Test health: {state.test_pass_rate * 100:.0f}% passing
- Has brain: {state.has_brain}

Generate 5 candidate actions. For each, provide:
- title: short action name
- category: feature|fix|debt|docs|infra|research|security|test
- description: what to do (1 sentence)
- expected_impact: 0-10 (how much does this move toward goal?)
- p_success: 0.0-1.0 (probability this works given current state)
- urgency: 0-10 (how bad if delayed 1 week?)
- cost: 1-10 (complexity + risk, higher = more costly)

Respond with ONLY valid JSON array, no markdown:
[{{"title":"...","category":"...","description":"...","expected_impact":7,"p_success":0.9,"urgency":6,"cost":3}}]"""

    try:
        result = subprocess.run(
            [CLAUDE_BIN, "--dangerously-skip-permissions", "--print", "-p", prompt],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            raw = result.stdout.strip()
            # Extract JSON array
            start = raw.find("[")
            end = raw.rfind("]") + 1
            if start >= 0 and end > start:
                data = json.loads(raw[start:end])
                return [
                    Action(
                        title=d.get("title", ""),
                        category=d.get("category", "feature"),
                        description=d.get("description", ""),
                        expected_impact=float(d.get("expected_impact", 5)),
                        p_success=float(d.get("p_success", 0.5)),
                        urgency=float(d.get("urgency", 5)),
                        cost=float(d.get("cost", 5)),
                    )
                    for d in data
                ]
    except Exception:
        pass

    # Fallback: stage-appropriate default candidates
    return _default_candidates(state)


def _default_candidates(state: ProjectState) -> list[Action]:
    """Stage-appropriate fallback candidates when LLM is unavailable."""
    base: list[Action] = []

    if state.test_pass_rate < 0.9:
        base.append(Action("fix-failing-tests", "fix",
            "Fix failing tests to restore test suite health",
            expected_impact=7, p_success=0.85, urgency=8, cost=3))

    if not state.has_brain:
        base.append(Action("setup-brain", "docs",
            "Set up .brain/ intelligence layer for this project",
            expected_impact=6, p_success=0.99, urgency=5, cost=1))

    if state.days_since_last_commit > 7:
        base.append(Action("resume-momentum", "feature",
            "Review open issues and make at least one meaningful commit",
            expected_impact=5, p_success=0.9, urgency=7, cost=2))

    if state.stage < 4:
        base.append(Action("core-functionality", "feature",
            "Implement the core feature that defines the project's value",
            expected_impact=9, p_success=0.7, urgency=9, cost=6))

    if state.stage > 6 and not state.open_issues:
        base.append(Action("reduce-tech-debt", "debt",
            "Address accumulated tech debt to improve maintainability",
            expected_impact=4, p_success=0.8, urgency=3, cost=4))

    if not base:
        base.append(Action("continue-roadmap", "feature",
            "Continue current roadmap phase",
            expected_impact=7, p_success=0.75, urgency=6, cost=5))

    return base


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _git_log(project_dir: Path) -> list[str]:
    try:
        r = subprocess.run(
            ["git", "log", "--oneline", "-10", "--no-decorate"],
            capture_output=True, text=True, timeout=5, cwd=str(project_dir)
        )
        return [l.strip() for l in r.stdout.strip().split("\n") if l.strip()]
    except Exception:
        return []


def _days_since_last_commit(project_dir: Path) -> int:
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            capture_output=True, text=True, timeout=5, cwd=str(project_dir)
        )
        ts = int(r.stdout.strip())
        now = int(datetime.now(timezone.utc).timestamp())
        return max(0, (now - ts) // 86400)
    except Exception:
        return 999


def _read_project_goal(project_dir: Path) -> str:
    for candidate in [
        project_dir / ".brain" / "memory" / "project_context.md",
        project_dir / "CLAUDE.md",
        project_dir / "README.md",
    ]:
        try:
            text = candidate.read_text(encoding="utf-8", errors="replace")
            lines = text.split("\n")
            for line in lines[:30]:
                if any(kw in line.lower() for kw in ["goal", "purpose", "objective", "what this"]):
                    stripped = line.strip("# ").strip()
                    if len(stripped) > 10:
                        return stripped[:200]
        except Exception:
            continue
    return "No goal defined — add to .brain/memory/project_context.md"


def _read_brain_decisions(project_dir: Path) -> list[str]:
    path = project_dir / ".brain" / "knowledge" / "decisions" / "log.md"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return [l.strip() for l in text.split("\n") if l.startswith("## DEC-")][:5]
    except Exception:
        return []


def _read_brain_skills(project_dir: Path) -> list[str]:
    path = project_dir / ".brain" / "knowledge" / "skills" / "skill-graph.md"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return [l.strip("## ").strip() for l in text.split("\n") if l.startswith("## ")][:5]
    except Exception:
        return []


def _detect_open_issues(project_dir: Path) -> list[str]:
    """Scan code for TODO/FIXME markers as proxy for open issues."""
    try:
        r = subprocess.run(
            ["grep", "-r", "--include=*.py", "--include=*.ts", "--include=*.js",
             "-l", r"TODO\|FIXME\|HACK\|XXX"],
            capture_output=True, text=True, timeout=10, cwd=str(project_dir)
        )
        files = [l.strip() for l in r.stdout.strip().split("\n") if l.strip()]
        return [f"TODOs in {f}" for f in files[:5]]
    except Exception:
        return []


def _estimate_test_health(project_dir: Path) -> float:
    """Estimate test pass rate without running tests (look at CI artifacts or test files)."""
    test_dirs = [project_dir / "tests", project_dir / "test", project_dir / "__tests__"]
    has_tests = any(d.exists() for d in test_dirs)
    if not has_tests:
        return 1.0  # No tests = no failures (benefit of the doubt)
    # Could run tests here but that's expensive — return neutral estimate
    return 0.85


def _estimate_stage(
    project_dir: Path,
    commits: list[str],
    days_since: int,
    has_brain: bool,
    has_planning: bool,
) -> float:
    score = 0.0

    # Commit history depth
    commit_count_estimate = min(10, len(commits)) / 10 * 3  # up to 3 points
    score += commit_count_estimate

    # Has README?
    if (project_dir / "README.md").exists():
        score += 1

    # Has tests?
    if any((project_dir / d).exists() for d in ["tests", "test", "__tests__"]):
        score += 1.5

    # Has CI?
    if (project_dir / ".github" / "workflows").exists():
        score += 1

    # Has brain?
    if has_brain:
        score += 0.5

    # Has planning?
    if has_planning:
        score += 0.5

    # Recent activity (penalize staleness)
    if days_since < 7:
        score += 0.5
    elif days_since > 30:
        score -= 0.5

    return max(0.0, min(10.0, score))


def _build_reasoning(state: ProjectState, top3: list[Action]) -> str:
    if not top3:
        return "No candidates to score."
    lines = [
        f"Project: {state.project_name} (stage={state.stage:.1f}/10 [{state.stage_label()}])",
        f"Goal: {state.goal}",
        "",
        "Top actions by Expected Value:",
    ]
    for i, a in enumerate(top3, 1):
        lines.append(
            f"  {i}. [{a.category}] {a.title} — EV={a.ev:.2f} "
            f"(impact={a.expected_impact}, p={a.p_success:.0%}, urgency={a.urgency}, cost={a.cost})"
        )
        lines.append(f"     {a.description}")
    return "\n".join(lines)


def _log_ranking(project_dir: Path, top5: list[Action], reasoning: str) -> None:
    """Append ranking to .brain/knowledge/daily/ for future learning."""
    brain_daily = project_dir / ".brain" / "knowledge" / "daily"
    if not brain_daily.exists():
        return
    d = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ts = datetime.now(timezone.utc).strftime("%H:%M UTC")
    daily = brain_daily / f"{d}.md"
    entry = f"\n\n## Probability Engine [{ts}]\n\n{reasoning}\n"
    try:
        if daily.exists():
            with open(daily, "a") as f:
                f.write(entry)
        else:
            with open(daily, "w") as f:
                f.write(f"# Daily Log — {d}\n{entry}")
    except Exception:
        pass


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Probability engine for compound-brain")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--output", choices=["text", "json"], default="text")
    args = parser.parse_args()

    print(f"[probability-engine] Analyzing {Path(args.project_dir).name}...")
    state = ProjectState.from_brain(Path(args.project_dir))

    print(f"  Stage: {state.stage:.1f}/10 ({state.stage_label()})")
    print(f"  Goal: {state.goal[:80]}")
    print(f"  Days since last commit: {state.days_since_last_commit}")
    print(f"  Generating action candidates...")

    result = rank_actions(state)

    if args.output == "json":
        print(json.dumps({
            "project": result.project,
            "stage": result.stage,
            "goal": result.goal,
            "top_action": asdict(result.top_action),
            "ranked": [asdict(a) for a in result.ranked],
            "reasoning": result.reasoning,
        }, indent=2, default=str))
    else:
        print(f"\n{result.reasoning}")
        print(f"\n→ RECOMMENDED: [{result.top_action.category}] {result.top_action.title}")
        print(f"  {result.top_action.description}")


if __name__ == "__main__":
    main()
