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

