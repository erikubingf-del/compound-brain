from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.department_cycle import run_department_cycle


class DepartmentCycleTests(unittest.TestCase):
    def test_cycle_blocks_when_approval_is_pending(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".brain" / "state" / "approval-state.json").write_text(
                json.dumps({"state": "awaiting-project-goal", "pending": ["project_goal"]})
            )

            result = run_department_cycle(repo, "architecture")

            self.assertEqual(result["status"], "blocked")
            self.assertEqual(result["reason"], "approval-pending")

    def test_cycle_writes_multi_department_mission_packet_and_handoffs(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".brain" / "state" / "approval-state.json").write_text(
                json.dumps({"state": "approved", "pending": []})
            )
            (repo / ".brain" / "state" / "action-queue.md").write_text("- Implement reporting export\n")
            (repo / ".claude" / "departments").mkdir(parents=True)
            (repo / ".claude" / "departments" / "engineering.md").write_text("# engineering\n")
            (repo / ".claude" / "departments" / "product.md").write_text("# product\n")
            (repo / ".claude" / "departments" / "operations.md").write_text("# operations\n")

            result = run_department_cycle(
                repo,
                "engineering",
                current_depth=4,
                goal="Ship a reliable reporting export",
                top_action="Implement reporting export",
                supporting_departments=["product", "operations"],
                skill_state={
                    "active": [{"title": "Debugging Reliability", "department": "engineering"}],
                    "missing": [{"title": "Product Documentation", "department": "product"}],
                },
            )

            self.assertEqual(result["status"], "ready")
            self.assertEqual(result["execution_class"], "implement")
            self.assertEqual(result["handoff_departments"], ["operations"])
            self.assertIn("write-product-brief", result["follow_up_actions"])
            mission_path = repo / ".brain" / "state" / "departments" / "engineering-mission.json"
            mission = json.loads(mission_path.read_text())
            self.assertEqual(mission["lead_department"], "engineering")
            self.assertEqual(mission["supporting_departments"], ["product", "operations"])
            self.assertEqual(mission["execution_class"], "implement")
            self.assertEqual(
                [stage["class"] for stage in mission["stages"]],
                ["analyze", "implement", "verify"],
            )
            self.assertEqual(mission["handoff_departments"], ["operations"])
