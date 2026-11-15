from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.prepare_brain import prepare_brain


class PrepareBrainTests(unittest.TestCase):
    def test_prepare_brain_writes_only_memory_and_codex_adapter(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)

            prepare_brain(repo)

            self.assertTrue((repo / "CLAUDE.md").exists())
            self.assertTrue((repo / ".brain").exists())
            self.assertTrue((repo / ".codex" / "AGENTS.md").exists())
            self.assertTrue((repo / "AGENTS.md").exists())
            self.assertIn("Codex Adapter", (repo / "AGENTS.md").read_text())
            self.assertIn("compound-brain codex adapter:begin", (repo / "AGENTS.md").read_text())
            skill = repo / ".agents" / "skills" / "project-brain" / "SKILL.md"
            self.assertTrue(skill.exists())
            self.assertIn("name: project-brain", skill.read_text())
            self.assertFalse((repo / ".claude").exists())

