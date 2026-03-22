from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch

from scripts.lib.runtime_heartbeat import RuntimeHeartbeatStore
from scripts.runtime_watchdog import main as runtime_watchdog_main


class RuntimeWatchdogTests(unittest.TestCase):
    def test_watchdog_reports_missing_and_healthy_repos(self) -> None:
        with TemporaryDirectory() as tmp:
            claude_home = Path(tmp) / ".claude"
            registry_dir = claude_home / "registry"
            registry_dir.mkdir(parents=True, exist_ok=True)
            repo_one = Path(tmp) / "repo-one"
            repo_two = Path(tmp) / "repo-two"
            repo_one.mkdir()
            repo_two.mkdir()
            (registry_dir / "activated-projects.json").write_text(
                json.dumps(
                    {
                        "projects": [
                            {"repo_path": str(repo_one), "repo_name": "repo-one"},
                            {"repo_path": str(repo_two), "repo_name": "repo-two"},
                        ]
                    },
                    indent=2,
                )
                + "\n"
            )

            store = RuntimeHeartbeatStore(registry_dir / "runtime-heartbeats", registry_dir / "runtime-locks")
            store.mark_start(repo_one, "cron")
            store.mark_success(repo_one, "cron", duration_seconds=1.0, summary="ok")

            with patch.dict("os.environ", {"COMPOUND_BRAIN_HOME": str(claude_home)}):
                rc = runtime_watchdog_main([])

            self.assertEqual(rc, 0)
            report = (claude_home / "knowledge" / "resources" / "runtime-heartbeats.md").read_text()
            self.assertIn("healthy: 1", report)
            self.assertIn("missing-heartbeat: 1", report)
