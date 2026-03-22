from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.skill_inventory import refresh_repo_skill_state


class SkillInventoryTests(unittest.TestCase):
    def test_refresh_repo_skill_state_tracks_active_stale_missing_and_materialized_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "demo-repo"
            repo.mkdir()

            (repo / ".brain" / "knowledge" / "skills" / "patterns").mkdir(parents=True)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".brain" / "autoresearch").mkdir(parents=True)
            (repo / ".claude").mkdir(parents=True)
            (repo / ".claude" / "settings.local.json").write_text(
                json.dumps(
                    {
                        "enabledDepartments": [
                            "architecture",
                            "engineering",
                            "operations",
                            "research",
                            "product",
                        ]
                    }
                )
            )
            (repo / "package.json").write_text("{}\n")
            (repo / "README.md").write_text("# Demo Repo\n")
            (repo / "src").mkdir()
            (repo / "src" / "App.tsx").write_text("export default function App() { return null; }\n")
            (repo / "tests").mkdir()
            (repo / ".github" / "workflows").mkdir(parents=True)
            (repo / ".brain" / "autoresearch" / "program.md").write_text("# Program\n")
            (repo / ".brain" / "knowledge" / "skills" / "skill-graph.md").write_text(
                "# Skill Graph\n\n"
                "## Debugging Reliability\n"
                "**Level:** Intermediate\n"
                "**Related Projects:** demo-repo\n"
                "**Key Knowledge:** Debugging code paths and improving reliability.\n"
                "**Next Improvements:** Connect reliability work to evaluations.\n\n"
                "## Legacy Terraform\n"
                "**Level:** Intermediate\n"
                "**Related Projects:** demo-repo\n"
                "**Key Knowledge:** Terraform module layout and infrastructure drift.\n"
                "**Next Improvements:** None.\n"
            )

            global_home = root / ".claude-home"
            (global_home / "knowledge" / "skills" / "patterns").mkdir(parents=True)
            (global_home / "knowledge" / "skills" / "skill-graph.md").write_text(
                "# Skill Graph\n\n"
                "## Release Operations\n"
                "**Level:** Advanced\n"
                "**Related Projects:** compound-brain\n"
                "**Key Knowledge:** Deploy, release, CI, and runtime safety controls.\n"
                "**Next Improvements:** Connect more repos to heartbeat review.\n"
            )
            (global_home / "knowledge" / "skills" / "patterns" / "release-operations.md").write_text(
                "# Release Operations\n\nUse guarded deploy and runtime review loops.\n"
            )

            approved_root = root / "approved-skills"
            (approved_root / "ui-master").mkdir(parents=True)
            (approved_root / "ui-master" / "SKILL.md").write_text(
                "---\n"
                "name: ui-master\n"
                "description: Production-grade UI design and frontend implementation for React and Next.js.\n"
                "---\n"
            )

            state = refresh_repo_skill_state(
                repo,
                claude_home=global_home,
                approved_external_roots=[approved_root],
            )

            active_titles = {item["title"] for item in state["active"]}
            self.assertIn("Debugging Reliability", active_titles)
            self.assertIn("Release Operations", active_titles)
            self.assertIn("ui-master", active_titles)
            self.assertIn("Legacy Terraform", {item["title"] for item in state["stale"]})
            self.assertIn("Product Documentation", {item["title"] for item in state["missing"]})
            self.assertEqual(
                {item["title"] for item in state["materialized"]},
                {"Release Operations", "ui-master"},
            )

            saved_state = json.loads((repo / ".brain" / "state" / "skills.json").read_text())
            self.assertEqual(saved_state["repo"], "demo-repo")
            self.assertTrue(
                (repo / ".brain" / "knowledge" / "skills" / "patterns" / "release-operations.md").exists()
            )
            self.assertTrue(
                (repo / ".brain" / "knowledge" / "skills" / "patterns" / "ui-master.md").exists()
            )
