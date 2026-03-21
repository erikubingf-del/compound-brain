from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.lib.skill_evolution import promote_skill_pattern


class SkillEvolutionTests(unittest.TestCase):
    def test_promote_skill_pattern_writes_pattern_and_updates_graph(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            graph = repo / ".brain" / "knowledge" / "skills" / "skill-graph.md"
            graph.parent.mkdir(parents=True, exist_ok=True)
            graph.write_text("# Skill Graph\n")

            promote_skill_pattern(
                repo=repo,
                skill_name="Approval-Gated Refactoring",
                related_projects=["demo"],
                key_knowledge="Only change owned surfaces after approval.",
                next_improvements="Tighten evaluator wiring.",
                pattern_body="# Pattern\n",
            )

            self.assertTrue(
                (
                    repo
                    / ".brain"
                    / "knowledge"
                    / "skills"
                    / "patterns"
                    / "approval-gated-refactoring.md"
                ).exists()
            )
            self.assertIn("Approval-Gated Refactoring", graph.read_text())

