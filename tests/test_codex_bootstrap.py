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
