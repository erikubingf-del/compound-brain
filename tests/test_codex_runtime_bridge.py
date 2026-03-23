from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch

from scripts.codex_runtime_bridge import ensure_codex_repo_runtime


class CodexRuntimeBridgeTests(unittest.TestCase):
    def test_bridge_reuses_fresh_runtime_state(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".claude").mkdir(parents=True)
            (repo / ".claude" / "settings.local.json").write_text("{}\n")
            (repo / ".brain" / "state" / "runtime-packet.json").write_text(
                json.dumps({"generated_at": "2099-03-23T12:00:00Z", "current_depth": 3}) + "\n"
            )
            (repo / ".brain" / "state" / "operator-recommendation.json").write_text(
                json.dumps({"recommended_next_action": "Refresh repo", "new_opportunities": []}) + "\n"
            )

            with patch("scripts.codex_runtime_bridge.run_project_runtime_event") as runtime_mock:
                result = ensure_codex_repo_runtime(repo, max_age_seconds=3600)

            self.assertEqual(result["status"], "fresh")
            self.assertEqual(result["recommended_next_action"], "Refresh repo")
            runtime_mock.assert_not_called()

    def test_bridge_runs_session_start_when_state_is_missing(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".claude").mkdir(parents=True)
            (repo / ".claude" / "settings.local.json").write_text("{}\n")

            with patch(
                "scripts.codex_runtime_bridge.run_project_runtime_event",
                return_value={"status": "ok", "event": "session-start"},
            ) as runtime_mock:
                result = ensure_codex_repo_runtime(repo, max_age_seconds=3600)

            self.assertEqual(result["status"], "ok")
            runtime_mock.assert_called_once()
