from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.department_arbitration import arbitrate_departments


class DepartmentArbitrationTests(unittest.TestCase):
    def test_arbitration_escalates_when_operations_is_blocked_on_infra_action(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".brain" / "state" / "departments").mkdir(parents=True)
            (repo / ".brain" / "state" / "departments" / "engineering.json").write_text(
                json.dumps({"status": "ready", "confidence_score": 0.8}) + "\n"
            )
            (repo / ".brain" / "state" / "departments" / "operations.json").write_text(
                json.dumps({"status": "blocked", "confidence_score": 0.4}) + "\n"
            )
            (repo / ".brain" / "state" / "departments" / "architecture.json").write_text(
                json.dumps({"status": "ready", "confidence_score": 0.8}) + "\n"
            )

            agreement = arbitrate_departments(
                repo=repo,
                event="cron",
                current_depth=3,
                lead_department="engineering",
                supporting_departments=["operations", "architecture"],
                top_action_category="infra",
                approval_state={"state": "approved", "pending": []},
            )

            self.assertEqual(agreement["result"], "escalate")
            self.assertEqual(agreement["positions"]["operations"], "object")
            self.assertTrue((repo / ".brain" / "state" / "department-agreement.json").exists())

    def test_arbitration_agrees_with_constraints_for_healthy_supporting_departments(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".brain" / "state" / "departments").mkdir(parents=True)
            for department in ["engineering", "product", "architecture"]:
                (repo / ".brain" / "state" / "departments" / f"{department}.json").write_text(
                    json.dumps({"status": "ready", "confidence_score": 0.8}) + "\n"
                )

            agreement = arbitrate_departments(
                repo=repo,
                event="user-request",
                current_depth=3,
                lead_department="engineering",
                supporting_departments=["product", "architecture"],
                top_action_category="feature",
                approval_state={"state": "approved", "pending": []},
            )

            self.assertEqual(agreement["result"], "agree-with-constraints")
