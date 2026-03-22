from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.materialize_project_claude import materialize_project_claude


class ProjectMaterializationTests(unittest.TestCase):
    def test_materialize_project_claude_creates_hooks_and_departments(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)

            materialize_project_claude(repo, ["architecture", "engineering"])

            self.assertTrue(
                (repo / ".claude" / "hooks" / "project_session_start.py").exists()
            )
            self.assertTrue(
                (repo / ".claude" / "departments" / "engineering.md").exists()
            )
            self.assertIn(
                "project_runtime_event.py",
                (repo / ".claude" / "hooks" / "project_session_start.py").read_text(),
            )
