from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.lib.codex_bootstrap import apply_managed_codex_block


class CodexBootstrapTests(unittest.TestCase):
    def test_apply_managed_codex_block_creates_global_agents_runtime_block(self) -> None:
        with TemporaryDirectory() as tmp:
            codex_home = Path(tmp) / ".codex"
            claude_home = Path(tmp) / ".claude"

            apply_managed_codex_block(codex_home / "AGENTS.md", claude_home)

            content = (codex_home / "AGENTS.md").read_text()
            self.assertIn("compound-brain managed runtime", content)
            self.assertIn("~/.claude/scripts/codex_runtime_bridge.py", content)
            self.assertIn("~/.claude/BRAIN.md", content)
            self.assertIn(".brain/state/operator-recommendation.json", content)
            self.assertIn("~/.codex/global-agent-governance.md", content)
            self.assertIn("regression tests", content)

    def test_refresh_preserves_custom_global_codex_instructions(self) -> None:
        with TemporaryDirectory() as tmp:
            codex_home = Path(tmp) / ".codex"
            claude_home = Path(tmp) / ".claude"
            codex_home.mkdir()
            agents = codex_home / "AGENTS.md"
            agents.write_text("# Personal rules\n\nKeep my project objectives.\n")

            apply_managed_codex_block(agents, claude_home)
            first = agents.read_text()
            self.assertIn("Keep my project objectives.", first)
            self.assertIn("global-agent-governance.md", first)

            apply_managed_codex_block(agents, claude_home)
            self.assertEqual(first, agents.read_text())
            self.assertEqual(first.count("<!-- compound-brain:begin -->"), 1)
