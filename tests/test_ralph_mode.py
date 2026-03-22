from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.lib.ralph_mode import build_ralph_decision, ensure_ralph_prd, run_ralph_loop


class RalphModeTests(unittest.TestCase):
    def test_build_ralph_decision_enables_compound_brain_feature_work(self) -> None:
        decision = build_ralph_decision(
            repo=Path("/tmp/compound-brain"),
            event="cron",
            current_depth=4,
            top_action="Implement runtime hardening lane",
            top_action_category="feature",
            approval_state={"state": "approved", "pending": []},
            governor={"trust_score": 82, "history": {"healthy_run_streak": 4}},
            agreement={"result": "agree"},
            policy={
                "enabled_for_compound_brain": True,
                "eligible_events": ["cron"],
                "min_depth": 4,
                "min_trust_score": 75,
                "required_healthy_streak": 3,
                "eligible_categories": ["feature", "debt", "research"],
                "preferred_agent": "codex",
                "default_prd_path": ".agents/tasks/prd-compound-brain-auto.json",
                "auto_create_prd": True,
            },
        )

        self.assertTrue(decision["eligible"])
        self.assertEqual(decision["mode"], "ralph")
        self.assertEqual(decision["agent"], "codex")

    def test_build_ralph_decision_blocks_non_compound_repo(self) -> None:
        decision = build_ralph_decision(
            repo=Path("/tmp/not-this-repo"),
            event="cron",
            current_depth=5,
            top_action="Implement runtime hardening lane",
            top_action_category="feature",
            approval_state={"state": "approved", "pending": []},
            governor={"trust_score": 99, "history": {"healthy_run_streak": 10}},
            agreement={"result": "agree"},
            policy={
                "enabled_for_compound_brain": True,
                "eligible_events": ["cron"],
                "min_depth": 4,
                "min_trust_score": 75,
                "required_healthy_streak": 3,
                "eligible_categories": ["feature", "debt", "research"],
            },
        )

        self.assertFalse(decision["eligible"])
        self.assertEqual(decision["mode"], "one-shot")
        self.assertIn("repo-not-self-hosting", decision["reasons"])

    def test_ensure_ralph_prd_materializes_auto_story(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp) / "compound-brain"
            repo.mkdir(parents=True)

            prd_path = ensure_ralph_prd(
                repo=repo,
                prd_path=repo / ".agents" / "tasks" / "prd-compound-brain-auto.json",
                top_action="Implement runtime hardening lane",
                goal="Keep the orchestrator self-improving without strategic drift",
                quality_gates=["python3 -m unittest discover -s tests -p 'test_*.py' -v", "bash install.sh --dry-run"],
            )

            payload = json.loads(prd_path.read_text())
            self.assertEqual(payload["project"], "compound-brain")
            self.assertEqual(payload["stories"][0]["status"], "open")
            self.assertIn("Implement runtime hardening lane", payload["stories"][0]["title"])

    def test_run_ralph_loop_invokes_single_iteration_with_prd(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp) / "compound-brain"
            repo.mkdir(parents=True)
            prd = ensure_ralph_prd(
                repo=repo,
                prd_path=repo / ".agents" / "tasks" / "prd-compound-brain-auto.json",
                top_action="Implement runtime hardening lane",
                goal="Keep the orchestrator self-improving without strategic drift",
                quality_gates=["python3 -m unittest discover -s tests -p 'test_*.py' -v"],
            )
            with patch("scripts.lib.ralph_mode.shutil.which", return_value="/opt/homebrew/bin/ralph"):
                with patch("scripts.lib.ralph_mode.subprocess.run") as run_mock:
                    summary = run_ralph_loop(
                        repo=repo,
                        prd_path=prd,
                        agent="codex",
                    )

            run_mock.assert_called_once()
            cmd = run_mock.call_args.args[0]
            self.assertEqual(cmd[:4], ["ralph", "build", "1", "--agent"])
            self.assertEqual(summary["status"], "executed")
            self.assertEqual(summary["mode"], "ralph")


if __name__ == "__main__":
    unittest.main()
