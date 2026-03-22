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

    def test_cycle_runs_evaluator_and_keeps_improved_metric(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".brain" / "autoresearch").mkdir(parents=True)
            (repo / ".brain" / "state" / "approval-state.json").write_text(
                json.dumps({"state": "approved", "pending": []})
            )
            (repo / ".brain" / "autoresearch" / "program.md").write_text(
                "# Program\n"
                "## Objective\nImprove evaluator score\n"
                "## Fixed Evaluator\nscore harness\n"
                "## Run Command\npython3 -c \"print(0.91)\"\n"
                "## Metric Extraction Rule\nstdout:number\n"
                "## Keep/Discard Rule\nhigher-is-better\n"
                "## Runtime Budget\n30\n"
            )
            (repo / ".brain" / "autoresearch" / "baseline.json").write_text(
                json.dumps({"baseline_metric": 0.50, "baseline_commit": "base"})
            )
            (repo / ".brain" / "autoresearch" / "queue.md").write_text("- Improve evaluator score\n")

            result = run_autoresearch_cycle(repo, "research")

            self.assertEqual(result["status"], "kept")
            self.assertEqual(result["reason"], "metric-improved")
            updated_baseline = json.loads((repo / ".brain" / "autoresearch" / "baseline.json").read_text())
            self.assertEqual(updated_baseline["baseline_metric"], 0.91)
