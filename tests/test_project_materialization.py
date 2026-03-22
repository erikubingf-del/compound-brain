from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.materialize_project_claude import materialize_project_claude
from scripts.lib.repo_profile import build_department_surfaces


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

    def test_materialize_project_claude_preserves_existing_claude_md_and_repo_surfaces(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".github" / "workflows").mkdir(parents=True)
            (repo / ".github" / "workflows" / "ci.yml").write_text("name: ci\n")
            (repo / "src").mkdir()
            (repo / "src" / "index.ts").write_text("export const ok = true;\n")
            (repo / "docs" / "crm-v2").mkdir(parents=True)
            (repo / "docs" / "crm-v2" / "overview.md").write_text("# CRM\n")
            (repo / "README.md").write_text("# Demo\n")
            (repo / "CLAUDE.md").write_text("# Existing Project Notes\n\nDo not delete this section.\n")

            departments = ["engineering", "operations", "product"]
            materialize_project_claude(
                repo,
                departments,
                department_surfaces=build_department_surfaces(repo, departments),
                department_goals={
                    "engineering": "Ship CRM code safely.",
                    "operations": "Keep deploy and CI safe.",
                    "product": "Keep CRM docs aligned.",
                },
            )

            claude_md = (repo / "CLAUDE.md").read_text()
            self.assertIn("Existing Project Notes", claude_md)
            self.assertIn("compound-brain managed block", claude_md)
            operations_md = (repo / ".claude" / "departments" / "operations.md").read_text()
            self.assertIn(".github/workflows", operations_md)
            self.assertIn("Keep deploy and CI safe.", operations_md)
            self.assertNotEqual(
                operations_md,
                (repo / ".claude" / "departments" / "engineering.md").read_text(),
            )
