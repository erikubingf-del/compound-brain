from pathlib import Path
from tempfile import TemporaryDirectory
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

