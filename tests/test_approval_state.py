from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.approval_state import ApprovalStateStore


class ApprovalStateTests(unittest.TestCase):
    def test_initialize_creates_pending_project_and_department_approval(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            store = ApprovalStateStore(repo / ".brain" / "state")

            state = store.initialize(
                project_goal_candidates=["Ship activation"],
                departments=["architecture", "engineering"],
            )

            self.assertEqual(state["state"], "awaiting-project-goal")
            self.assertIn("project_goal", state["pending"])
            self.assertIn("department_goals", state["pending"])

    def test_initialize_persists_recommendation_for_goal_and_departments(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            store = ApprovalStateStore(repo / ".brain" / "state")

            state = store.initialize(
                project_goal_candidates=["Ship activation"],
                departments=["architecture", "engineering"],
                recommendation={
                    "message": "Before confirming goals, write a proper project_goal and align departments.",
                    "recommended_project_goal": "Operate this as a trading system with evaluator-backed execution.",
                    "recommended_departments": ["D01", "D02", "D03"],
                },
            )

            stored = json.loads((repo / ".brain" / "state" / "approval-state.json").read_text())
            self.assertEqual(stored["recommendation"]["recommended_departments"], ["D01", "D02", "D03"])
            self.assertIn("trading system", stored["recommendation"]["recommended_project_goal"])
            pending_md = (repo / ".brain" / "state" / "pending-approvals.md").read_text()
            self.assertIn("## Recommendation", pending_md)
            self.assertIn("Want me to do that?", pending_md)

    def test_confirm_strategy_persists_goal_and_departments(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            store = ApprovalStateStore(repo / ".brain" / "state")
            store.initialize(
                project_goal_candidates=["Ship activation"],
                departments=["architecture", "engineering"],
            )

            state = store.confirm_strategy(
                project_goal="Ship CRM V2 reliably",
                departments=["engineering", "product", "operations"],
            )

            self.assertEqual(state["state"], "approved")
            self.assertEqual(state["pending"], [])
            self.assertEqual(state["project_goal"], "Ship CRM V2 reliably")
            self.assertEqual(state["departments"], ["engineering", "product", "operations"])
