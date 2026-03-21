from __future__ import annotations


def recommended_lane(cost: float) -> str:
    return "worktree" if cost >= 5 else "branch"


def gating_status(action: dict) -> str:
    if "gating_status" in action:
        return str(action["gating_status"])
    if action.get("requires_confirmation"):
        return "awaiting-strategic-confirmation"
    return "ready-for-bounded-execution"


def score_action(action: dict) -> float:
    evidence_quality = float(action.get("evidence_quality", 1.0))
    goal_alignment = float(action.get("goal_alignment", 0))
    probability = float(action.get("probability", 0))
    urgency = float(action.get("urgency", 0))
    cost = max(float(action.get("cost", 1)), 1.0)
    return goal_alignment * probability * urgency * evidence_quality / cost


def rank_actions(actions: list[dict]) -> list[dict]:
    ranked = []
    for action in actions:
        row = dict(action)
        row["score"] = round(score_action(action), 3)
        row["recommended_lane"] = str(
            action.get("recommended_lane", recommended_lane(float(action.get("cost", 1))))
        )
        row["gating_status"] = gating_status(action)
        ranked.append(row)
    return sorted(ranked, key=lambda item: item["score"], reverse=True)


def format_ranked_actions(actions: list[dict]) -> str:
    lines = []
    for index, action in enumerate(actions, start=1):
        lines.append(f"{index}. {action['title']}")
        lines.append(f"Department: {action.get('department', 'unassigned')}")
        lines.append(f"Why: {action.get('why', 'No rationale provided.')}")
        lines.append(f"Score: {action['score']}")
        lines.append(f"Gating: {action['gating_status']}")
        lines.append(f"Lane: {action['recommended_lane']}")
        lines.append("")
    return "\n".join(lines).rstrip()
