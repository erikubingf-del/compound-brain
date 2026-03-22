import os
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import unittest
from unittest.mock import patch

from scripts.lib.runtime_heartbeat import RuntimeHeartbeatStore
from scripts.project_runtime_event import run_project_runtime_event


class ProjectRuntimeEventTests(unittest.TestCase):
    def test_runtime_cli_is_silent_by_default_for_hook_use(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=str(repo), check=False, capture_output=True, text=True)
            (repo / ".brain" / "knowledge" / "projects").mkdir(parents=True)
            (repo / ".brain" / "memory").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "daily").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "decisions").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "skills").mkdir(parents=True)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".claude").mkdir(parents=True)
            (repo / ".claude" / "settings.local.json").write_text(json.dumps({"enabledDepartments": ["engineering"]}))
            (repo / ".brain" / "state" / "approval-state.json").write_text(json.dumps({"state": "approved", "pending": []}))
            (repo / ".brain" / "MEMORY.md").write_text("# Memory\n")
            (repo / ".brain" / "memory" / "project_context.md").write_text("# Context\n")
            (repo / ".brain" / "memory" / "feedback_rules.md").write_text("# Feedback\n")
            (repo / ".brain" / "knowledge" / "projects" / f"{repo.name}.md").write_text("# Project\n")
            (repo / "CLAUDE.md").write_text("# Demo\n\n## Goal\nShip a demo.\n")
            (repo / "README.md").write_text("# Demo\n")
            script = Path(__file__).resolve().parents[1] / "scripts" / "project_runtime_event.py"
            env = dict(os.environ)
            env["COMPOUND_BRAIN_HOME"] = str(repo / ".global-brain")
            result = subprocess.run(
                ["python3", str(script), "--event", "stop", "--project-dir", str(repo)],
                cwd=str(Path(__file__).resolve().parents[1]),
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertEqual(result.stdout, "")

    def test_runtime_cli_can_emit_valid_json_on_demand(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=str(repo), check=False, capture_output=True, text=True)
            (repo / ".brain" / "knowledge" / "projects").mkdir(parents=True)
            (repo / ".brain" / "memory").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "daily").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "decisions").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "skills").mkdir(parents=True)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".claude").mkdir(parents=True)
            (repo / ".claude" / "settings.local.json").write_text(json.dumps({"enabledDepartments": ["engineering"]}))
            (repo / ".brain" / "state" / "approval-state.json").write_text(json.dumps({"state": "approved", "pending": []}))
            (repo / ".brain" / "MEMORY.md").write_text("# Memory\n")
            (repo / ".brain" / "memory" / "project_context.md").write_text("# Context\n")
            (repo / ".brain" / "memory" / "feedback_rules.md").write_text("# Feedback\n")
            (repo / ".brain" / "knowledge" / "projects" / f"{repo.name}.md").write_text("# Project\n")
            (repo / "CLAUDE.md").write_text("# Demo\n\n## Goal\nShip a demo.\n")
            (repo / "README.md").write_text("# Demo\n")
            script = Path(__file__).resolve().parents[1] / "scripts" / "project_runtime_event.py"
            env = dict(os.environ)
            env["COMPOUND_BRAIN_HOME"] = str(repo / ".global-brain")
            result = subprocess.run(
                ["python3", str(script), "--event", "stop", "--project-dir", str(repo), "--json-output"],
                cwd=str(Path(__file__).resolve().parents[1]),
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")

    def test_session_start_refreshes_brief_and_action_queue_for_activated_repo(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=str(repo), check=False, capture_output=True, text=True)
            (repo / ".brain" / "knowledge" / "projects").mkdir(parents=True)
            (repo / ".brain" / "memory").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "daily").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "decisions").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "skills").mkdir(parents=True)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".claude").mkdir(parents=True)
            (repo / ".claude" / "settings.local.json").write_text(json.dumps({"enabledDepartments": ["engineering"]}))
            (repo / ".brain" / "state" / "approval-state.json").write_text(json.dumps({"state": "approved", "pending": []}))
            (repo / ".brain" / "MEMORY.md").write_text("# Memory\n")
            (repo / ".brain" / "memory" / "project_context.md").write_text("# Context\n")
            (repo / ".brain" / "memory" / "feedback_rules.md").write_text("# Feedback\n")
            (repo / ".brain" / "knowledge" / "projects" / f"{repo.name}.md").write_text("# Project\n")
            (repo / "CLAUDE.md").write_text("# Demo\n\n## Goal\nShip a demo.\n")
            (repo / "README.md").write_text("# Demo\n")
            with patch.dict("os.environ", {"COMPOUND_BRAIN_HOME": str(repo / ".global-brain")}):
                result = run_project_runtime_event(repo, "session-start")

            self.assertEqual(result["status"], "ok")
            self.assertTrue((repo / ".brain" / "knowledge" / "daily" / "intelligence_brief_latest.md").exists())
            self.assertTrue((repo / ".brain" / "state" / "action-queue.md").exists())
            self.assertTrue((repo / ".brain" / "state" / "skills.json").exists())
            self.assertTrue((repo / ".brain" / "state" / "context-snapshot.json").exists())
            self.assertTrue((repo / ".brain" / "state" / "runtime-packet.json").exists())
            store = RuntimeHeartbeatStore(repo / ".global-brain" / "registry" / "runtime-heartbeats", repo / ".global-brain" / "registry" / "runtime-locks")
            self.assertEqual(store.load(repo)["events"]["session-start"]["status"], "ok")

    def test_cron_runs_project_cron_for_activated_repo(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=str(repo), check=False, capture_output=True, text=True)
            (repo / ".brain" / "memory").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "daily").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "decisions").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "skills").mkdir(parents=True)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "projects").mkdir(parents=True)
            (repo / ".claude" / "departments").mkdir(parents=True)
            (repo / ".claude").mkdir(parents=True, exist_ok=True)
            (repo / ".claude" / "settings.local.json").write_text(json.dumps({"enabledDepartments": ["research"]}))
            (repo / ".claude" / "departments" / "research.md").write_text("# Research\n")
            (repo / ".brain" / "state" / "approval-state.json").write_text(json.dumps({"state": "approved", "pending": []}))
            (repo / ".brain" / "state" / "autonomy-depth.json").write_text(
                json.dumps({"current_depth": 4, "allowed_max_depth": 5, "user_max_depth": 5, "recommended_next_depth": 5, "consecutive_healthy_cycles": 0}) + "\n"
            )
            (repo / ".brain" / "state" / "runtime-governor.json").write_text("{}\n")
            (repo / ".brain" / "MEMORY.md").write_text("# Memory\n")
            (repo / ".brain" / "memory" / "project_context.md").write_text("# Context\n")
            (repo / ".brain" / "memory" / "feedback_rules.md").write_text("# Feedback\n")
            (repo / ".brain" / "knowledge" / "projects" / f"{repo.name}.md").write_text("# Project\n")
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

    def test_cron_depth_two_stays_in_planning_mode(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=str(repo), check=False, capture_output=True, text=True)
            (repo / ".brain" / "memory").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "daily").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "decisions").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "skills").mkdir(parents=True)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".claude").mkdir(parents=True, exist_ok=True)
            (repo / ".claude" / "settings.local.json").write_text(json.dumps({"enabledDepartments": ["research"]}))
            (repo / ".brain" / "state" / "approval-state.json").write_text(json.dumps({"state": "approved", "pending": []}))
            (repo / ".brain" / "state" / "autonomy-depth.json").write_text(
                json.dumps({"current_depth": 2, "allowed_max_depth": 5, "user_max_depth": 5, "recommended_next_depth": 3, "consecutive_healthy_cycles": 0}) + "\n"
            )
            (repo / ".brain" / "autoresearch").mkdir(parents=True)
            (repo / ".brain" / "autoresearch" / "program.md").write_text("# Program\n")
            (repo / "CLAUDE.md").write_text("# Demo\n\n## Goal\nShip a demo.\n")
            (repo / "README.md").write_text("# Demo\n")
            with patch.dict("os.environ", {"COMPOUND_BRAIN_HOME": str(repo / ".global-brain")}):
                result = run_project_runtime_event(repo, "cron")

            self.assertEqual(result["status"], "ok")
            self.assertIn("planning-only", result["cron_summary"])

    def test_cron_escalates_when_operations_objects_to_infra_work(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=str(repo), check=False, capture_output=True, text=True)
            (repo / ".brain" / "memory").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "daily").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "decisions").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "skills").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "projects").mkdir(parents=True)
            (repo / ".brain" / "state" / "departments").mkdir(parents=True)
            (repo / ".brain" / "state").mkdir(parents=True, exist_ok=True)
            (repo / ".brain" / "MEMORY.md").write_text("# Memory\n")
            (repo / ".brain" / "memory" / "project_context.md").write_text("# Context\n")
            (repo / ".brain" / "memory" / "feedback_rules.md").write_text("# Feedback\n")
            (repo / ".brain" / "knowledge" / "projects" / f"{repo.name}.md").write_text("# Project\n")
            (repo / ".brain" / "state" / "departments" / "engineering.json").write_text(
                json.dumps({"status": "ready", "confidence_score": 0.8}) + "\n"
            )
            (repo / ".brain" / "state" / "departments" / "operations.json").write_text(
                json.dumps({"status": "blocked", "confidence_score": 0.3}) + "\n"
            )
            (repo / ".brain" / "state" / "departments" / "architecture.json").write_text(
                json.dumps({"status": "ready", "confidence_score": 0.8}) + "\n"
            )
            (repo / ".claude" / "departments").mkdir(parents=True)
            (repo / ".claude").mkdir(parents=True, exist_ok=True)
            (repo / ".claude" / "settings.local.json").write_text(
                json.dumps({"enabledDepartments": ["engineering", "operations", "architecture"]})
            )
            for department in ["engineering", "operations", "architecture"]:
                (repo / ".claude" / "departments" / f"{department}.md").write_text(f"# {department}\n")
            (repo / ".brain" / "state" / "approval-state.json").write_text(json.dumps({"state": "approved", "pending": []}))
            (repo / ".brain" / "state" / "autonomy-depth.json").write_text(
                json.dumps({"current_depth": 3, "allowed_max_depth": 5, "user_max_depth": 5, "recommended_next_depth": 4, "consecutive_healthy_cycles": 0}) + "\n"
            )
            (repo / "CLAUDE.md").write_text("# Demo\n\n## Goal\nShip a demo.\n")
            (repo / "README.md").write_text("# Demo\n")

            with patch.dict("os.environ", {"COMPOUND_BRAIN_HOME": str(repo / ".global-brain")}):
                with patch("scripts.project_runtime_event.refresh_ranked_actions", return_value={"top_action": "Deploy runtime fix", "top_action_category": "infra", "goal": "Ship"}):
                    result = run_project_runtime_event(repo, "cron")

            self.assertEqual(result["status"], "ok")
            self.assertIn("arbitration=escalate", result["cron_summary"])

    def test_cron_failure_records_backoff_heartbeat(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=str(repo), check=False, capture_output=True, text=True)
            (repo / ".brain" / "state").mkdir(parents=True)
            (repo / ".brain" / "memory").mkdir(parents=True)
            (repo / ".claude").mkdir(parents=True)
            (repo / ".claude" / "settings.local.json").write_text(json.dumps({"enabledDepartments": ["engineering"]}))
            (repo / ".brain" / "state" / "approval-state.json").write_text(json.dumps({"state": "approved", "pending": []}))

            with patch.dict("os.environ", {"COMPOUND_BRAIN_HOME": str(repo / ".global-brain")}):
                with patch("scripts.project_runtime_event.run_for_project", return_value="ok"):
                    with patch("scripts.project_runtime_event.refresh_ranked_actions", return_value={"top_action": "do-x", "goal": "ship"}):
                        with patch("scripts.project_runtime_event.run_project_cron", side_effect=RuntimeError("boom")):
                            result = run_project_runtime_event(repo, "cron")

            self.assertEqual(result["status"], "failed")
            store = RuntimeHeartbeatStore(repo / ".global-brain" / "registry" / "runtime-heartbeats", repo / ".global-brain" / "registry" / "runtime-locks")
            cron = store.load(repo)["events"]["cron"]
            self.assertEqual(cron["status"], "failed")
            self.assertEqual(cron["backoff_minutes"], 15)

    def test_compound_brain_cron_autoroutes_to_ralph_when_eligible(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp) / "compound-brain"
            repo.mkdir(parents=True)
            subprocess.run(["git", "init"], cwd=str(repo), check=False, capture_output=True, text=True)
            (repo / ".brain" / "memory").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "daily").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "decisions").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "skills").mkdir(parents=True)
            (repo / ".brain" / "knowledge" / "projects").mkdir(parents=True)
            (repo / ".brain" / "state" / "departments").mkdir(parents=True)
            (repo / ".brain" / "state").mkdir(parents=True, exist_ok=True)
            (repo / ".brain" / "MEMORY.md").write_text("# Memory\n")
            (repo / ".brain" / "memory" / "project_context.md").write_text("# Context\n")
            (repo / ".brain" / "memory" / "feedback_rules.md").write_text("# Feedback\n")
            (repo / ".brain" / "knowledge" / "projects" / f"{repo.name}.md").write_text("# Project\n")
            (repo / ".brain" / "state" / "departments" / "engineering.json").write_text(
                json.dumps({"status": "ready", "confidence_score": 0.9}) + "\n"
            )
            (repo / ".brain" / "state" / "departments" / "architecture.json").write_text(
                json.dumps({"status": "ready", "confidence_score": 0.9}) + "\n"
            )
            (repo / ".claude" / "departments").mkdir(parents=True)
            (repo / ".claude" / "settings.local.json").write_text(
                json.dumps({"enabledDepartments": ["engineering", "architecture"]})
            )
            for department in ["engineering", "architecture"]:
                (repo / ".claude" / "departments" / f"{department}.md").write_text(f"# {department}\n")
            (repo / ".brain" / "state" / "approval-state.json").write_text(json.dumps({"state": "approved", "pending": []}))
            (repo / ".brain" / "state" / "autonomy-depth.json").write_text(
                json.dumps({"current_depth": 4, "allowed_max_depth": 5, "user_max_depth": 5, "recommended_next_depth": 5, "consecutive_healthy_cycles": 4}) + "\n"
            )
            (repo / ".brain" / "state" / "runtime-governor.json").write_text(
                json.dumps({"trust_score": 82, "history": {"healthy_run_streak": 4}}) + "\n"
            )
            (repo / ".brain" / "autoresearch").mkdir(parents=True)
            (repo / ".brain" / "autoresearch" / "program.md").write_text("# Program\n")
            (repo / "CLAUDE.md").write_text("# Demo\n\n## Goal\nShip a demo.\n")
            (repo / "README.md").write_text("# Demo\n")

            with patch.dict("os.environ", {"COMPOUND_BRAIN_HOME": str(repo / ".global-brain")}):
                with patch("scripts.project_runtime_event.refresh_ranked_actions", return_value={"top_action": "Implement runtime hardening lane", "top_action_category": "feature", "goal": "Keep the orchestrator self-improving"}):
                    with patch("scripts.project_runtime_event.run_ralph_loop", return_value={"status": "executed", "mode": "ralph", "agent": "codex"}) as run_ralph_mock:
                        with patch("scripts.project_runtime_event.run_project_cron") as run_project_cron_mock:
                            result = run_project_runtime_event(repo, "cron")

            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["execution_mode"], "ralph")
            self.assertIn("ralph=executed", result["cron_summary"])
            run_ralph_mock.assert_called_once()
            run_project_cron_mock.assert_not_called()
