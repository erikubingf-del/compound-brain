from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from scripts.lib.runtime_governor import (
    build_context_snapshot,
    build_runtime_governor,
    build_runtime_packet,
)


class RuntimeGovernorTests(unittest.TestCase):
    def test_build_context_snapshot_marks_context_complete(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".brain" / "memory").mkdir(parents=True)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".claude" / "departments").mkdir(parents=True)
            (repo / "CLAUDE.md").write_text("# Demo\n")
            (repo / ".brain" / "MEMORY.md").write_text("# Memory\n")
            (repo / ".brain" / "memory" / "project_context.md").write_text("# Context\n")
            (repo / ".brain" / "memory" / "feedback_rules.md").write_text("# Feedback\n")
            (repo / ".brain" / "state" / "action-queue.md").write_text("# Queue\n")
            (repo / ".brain" / "state" / "skills.json").write_text('{"active": [], "missing": []}\n')
            (repo / ".brain" / "state" / "approval-state.json").write_text('{"state":"approved","pending":[]}\n')
            (repo / ".claude" / "settings.local.json").write_text("{}\n")
            (repo / ".claude" / "departments" / "engineering.md").write_text("# Engineering\n")

            snapshot = build_context_snapshot(
                repo,
                event="session-start",
                current_depth=3,
                required_files=[
                    repo / "CLAUDE.md",
                    repo / ".brain" / "MEMORY.md",
                    repo / ".brain" / "memory" / "project_context.md",
                    repo / ".brain" / "memory" / "feedback_rules.md",
                    repo / ".brain" / "state" / "action-queue.md",
                    repo / ".brain" / "state" / "skills.json",
                    repo / ".brain" / "state" / "approval-state.json",
                    repo / ".claude" / "settings.local.json",
                    repo / ".claude" / "departments" / "engineering.md",
                ],
            )

            self.assertTrue(snapshot["context_ok"])
            self.assertFalse(snapshot["missing_context_files"])

    def test_build_runtime_governor_scores_repo_and_flags_raise_readiness(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".brain" / "state" / "departments").mkdir(parents=True)
            (repo / ".brain" / "state" / "departments" / "engineering.json").write_text(
                json.dumps({"status": "ready"}) + "\n"
            )
            governor = build_runtime_governor(
                repo=repo,
                event="session-start",
                current_depth=2,
                approval_state={"state": "approved", "pending": []},
                context_snapshot={"context_ok": True},
                skill_state={"active": [{"title": "ui-master"}], "missing": []},
                heartbeat_record={"events": {"cron": {"status": "ok"}}},
                policy={"raise_thresholds": {"3": 60}, "stay_floors": {"2": 25}},
                validation_success=0.9,
            )

            self.assertGreaterEqual(governor["trust_score"], 60)
            self.assertTrue(governor["readiness"]["can_raise_to_3"])

    def test_build_runtime_packet_carries_loaded_context_and_action_bounds(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            packet = build_runtime_packet(
                repo=repo,
                event="session-start",
                current_depth=3,
                lead_department="engineering",
                supporting_departments=["architecture"],
                goal="Ship safely",
                top_action="Fix nav bug",
                approval_state={"state": "approved", "pending": []},
                skill_state={"active": [{"title": "systematic-debugging"}], "missing": [{"title": "Release Operations"}]},
                context_snapshot={
                    "context_ok": True,
                    "required_context_files": ["CLAUDE.md"],
                    "loaded_context_files": ["CLAUDE.md"],
                    "missing_context_files": [],
                },
                allowed_actions=["bounded-edit", "validation"],
                blocked_actions=["autoresearch"],
                do_not_repeat=["Do not repeat nav regression"],
            )

            self.assertEqual(packet["lead_department"], "engineering")
            self.assertTrue(packet["context_ok"])
            self.assertIn("bounded-edit", packet["allowed_actions"])
