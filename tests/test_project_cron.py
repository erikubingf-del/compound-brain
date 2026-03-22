from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.run_project_llm_cron import run_project_cron


class ProjectCronTests(unittest.TestCase):
    def test_run_project_cron_executes_autoresearch_when_program_exists(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".claude").mkdir(parents=True)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".brain" / "autoresearch").mkdir(parents=True)
            (repo / ".claude" / "settings.local.json").write_text(
                json.dumps({"enabledDepartments": ["research"]})
            )
            (repo / ".brain" / "state" / "approval-state.json").write_text(
                json.dumps({"state": "approved", "pending": []})
            )
            (repo / ".brain" / "autoresearch" / "program.md").write_text(
                "# Program\n"
                "## Objective\nImprove metric\n"
                "## Fixed Evaluator\nscore harness\n"
                "## Run Command\npython3 -c \"print(0.75)\"\n"
                "## Metric Extraction Rule\nstdout:number\n"
                "## Keep/Discard Rule\nhigher-is-better\n"
                "## Runtime Budget\n30\n"
            )
            (repo / ".brain" / "autoresearch" / "queue.md").write_text("- Improve metric\n")

            output, rc = run_project_cron(repo)

            self.assertEqual(rc, 0)
            self.assertIn("autoresearch=baseline-recorded", output)
            self.assertTrue((repo / ".brain" / "autoresearch" / "results.jsonl").exists())
