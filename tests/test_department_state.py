from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.department_state import initialize_department_state


class DepartmentStateTests(unittest.TestCase):
    def test_initialize_department_state_creates_json_for_each_department(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)

            initialize_department_state(repo, ["architecture", "engineering"])

            state_path = repo / ".brain" / "state" / "departments" / "architecture.json"
            self.assertTrue(state_path.exists())
            payload = json.loads(state_path.read_text())
            self.assertEqual(payload["status"], "idle")
            self.assertEqual(payload["approval_state"], "pending")
            self.assertTrue(
                (repo / ".brain" / "knowledge" / "departments" / "architecture-sources.md").exists()
            )
            self.assertTrue(
                (repo / ".brain" / "state" / "departments" / "architecture-shopping.json").exists()
            )
