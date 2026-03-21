from __future__ import annotations


def infer_departments(
    tech_stack: list[str],
    docs_present: bool,
    ci_present: bool,
) -> list[str]:
    departments = ["architecture", "engineering"]
    if docs_present:
        departments.append("product")
    if ci_present or "Docker" in tech_stack or "GitHub Actions" in tech_stack:
        departments.append("operations")
    if any(tech in tech_stack for tech in ["Python", "TypeScript", "JavaScript"]):
        departments.append("research")
    return departments


def build_audit_packet(
    repo_name: str,
    tech_stack: list[str],
    docs_present: bool,
    ci_present: bool,
) -> dict:
    departments = infer_departments(tech_stack, docs_present, ci_present)
    return {
        "repo_name": repo_name,
        "project_goal_candidates": [
            f"Clarify and accelerate the highest-probability path for {repo_name}",
            f"Turn {repo_name} into a goal-driven repo with persistent memory and bounded autonomy",
        ],
        "departments": departments,
        "department_goals": {
            department: f"Improve {repo_name} through {department}-led decisions and execution"
            for department in departments
        },
        "proposed_architecture_changes": [
            "Write audit outputs into repo-local state files that survive across sessions",
            "Confirm strategic goals before enabling repeated autonomous execution",
        ],
        "risks": [
            "Project goal may be under-specified until the first strategic confirmation",
            "Autonomous loops can drift if department boundaries are not explicit",
        ],
        "candidate_actions": [
            {
                "title": "Confirm project goal and department goals",
                "why": "Autonomous execution needs an explicit direction before it can optimize next moves.",
                "effort": "S",
            },
            {
                "title": "Materialize repo-local .claude and .brain state surfaces",
                "why": "The repo needs durable control surfaces for hooks, memory, and department ownership.",
                "effort": "M",
            },
            {
                "title": "Rank the first bounded execution candidates",
                "why": "A logged action queue turns the audit into operational next steps.",
                "effort": "S",
            },
        ],
    }
