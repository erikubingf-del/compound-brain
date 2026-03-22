from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import unittest
from unittest.mock import patch

from scripts.project_runtime_event import run_project_runtime_event


class ProjectRuntimeEventTests(unittest.TestCase):
    def test_session_start_refreshes_brief_and_action_queue_for_activated_repo(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=str(repo), check=False, capture_output=True, text=True)
            (repo / ".brain" / "memory").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "daily").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "decisions").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "skills").mkdir(parents=True)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".claude").mkdir(parents=True)
            (repo / ".claude" / "settings.local.json").write_text(json.dumps({"enabledDepartments": ["engineering"]}))
            (repo / ".brain" / "state" / "approval-state.json").write_text(json.dumps({"state": "approved", "pending": []}))
            (repo / "CLAUDE.md").write_text("# Demo\n\n## Goal\nShip a demo.\n")
            (repo / "README.md").write_text("# Demo\n")
            with patch.dict("os.environ", {"COMPOUND_BRAIN_HOME": str(repo / ".global-brain")}):
                result = run_project_runtime_event(repo, "session-start")

            self.assertEqual(result["status"], "ok")
            self.assertTrue((repo / ".brain" / "knowledge" / "daily" / "intelligence_brief_latest.md").exists())
            self.assertTrue((repo / ".brain" / "state" / "action-queue.md").exists())

    def test_cron_runs_project_cron_for_activated_repo(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=str(repo), check=False, capture_output=True, text=True)
            (repo / ".brain" / "memory").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "daily").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "decisions").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "skills").mkdir(parents=True)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".claude" / "departments").mkdir(parents=True)
            (repo / ".claude").mkdir(parents=True, exist_ok=True)
            (repo / ".claude" / "settings.local.json").write_text(json.dumps({"enabledDepartments": ["research"]}))
            (repo / ".brain" / "state" / "approval-state.json").write_text(json.dumps({"state": "approved", "pending": []}))
            (repo / ".brain" / "autoresearch").mkdir(parents=True)
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
            (repo / "CLAUDE.md").write_text("# Demo\n\n## Goal\nShip a demo.\n")
            (repo / "README.md").write_text("# Demo\n")
            with patch.dict("os.environ", {"COMPOUND_BRAIN_HOME": str(repo / ".global-brain")}):
                result = run_project_runtime_event(repo, "cron")

            self.assertEqual(result["status"], "ok")
            self.assertIn("autoresearch", result["cron_summary"])
