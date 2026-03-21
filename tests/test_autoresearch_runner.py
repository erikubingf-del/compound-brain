from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.autoresearch_runner import run_autoresearch_cycle


class AutoresearchRunnerTests(unittest.TestCase):
    def test_cycle_refuses_to_run_without_autoresearch_approval(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".brain" / "autoresearch").mkdir(parents=True)
            (repo / ".brain" / "state" / "approval-state.json").write_text(
                json.dumps({"state": "awaiting-autoresearch-enable", "pending": ["autoresearch_enable"]})
            )

            result = run_autoresearch_cycle(repo, "research")

            self.assertEqual(result["status"], "blocked")
            self.assertEqual(result["reason"], "autoresearch-not-approved")

