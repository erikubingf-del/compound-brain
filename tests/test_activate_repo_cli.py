from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import subprocess
import unittest


class ActivateRepoCliTests(unittest.TestCase):
    def test_activate_repo_help_lists_lifecycle_steps(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/activate_repo.py", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertIn("observe", result.stdout.lower())
        self.assertIn("prepare", result.stdout.lower())

    def test_activate_repo_creates_approval_state_for_prepared_repo(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            (repo / "README.md").write_text("# demo\n")
            subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.com",
                    "commit",
                    "-qm",
                    "init",
                ],
                cwd=repo,
                check=True,
            )

            env = os.environ.copy()
            env["COMPOUND_BRAIN_HOME"] = str(Path(tmp) / "claude-home")
            result = subprocess.run(
                ["python3", "scripts/activate_repo.py", "--project-dir", str(repo)],
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("repo: demo", result.stdout)
            self.assertTrue((repo / ".brain" / "state" / "approval-state.json").exists())
            self.assertTrue((repo / ".brain" / "state" / "autonomy-depth.json").exists())
            self.assertTrue((repo / ".brain" / "state" / "runtime-governor.json").exists())
            self.assertTrue((repo / ".claude").exists())
            state = json.loads((repo / ".brain" / "state" / "approval-state.json").read_text())
            self.assertEqual(state["state"], "awaiting-project-goal")

    def test_activate_repo_prints_domain_specific_recommendation_before_confirmation(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo-trading"
            repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            (repo / "README.md").write_text(
                "# Demo Trading\n\n"
                "This trading system coordinates D01 market-structure, D02 execution, and D03 risk.\n"
            )
            subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.com",
                    "commit",
                    "-qm",
                    "init",
                ],
                cwd=repo,
                check=True,
            )

            env = os.environ.copy()
            env["COMPOUND_BRAIN_HOME"] = str(Path(tmp) / "claude-home")
            result = subprocess.run(
                ["python3", "scripts/activate_repo.py", "--project-dir", str(repo)],
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("Recommendation:", result.stdout)
            self.assertIn("project_goal", result.stdout)
            self.assertIn("D01–D03", result.stdout)
            self.assertIn("Want me to do that?", result.stdout)
            state = json.loads((repo / ".brain" / "state" / "approval-state.json").read_text())
            self.assertEqual(state["recommendation"]["recommended_departments"], ["D01", "D02", "D03"])

    def test_activate_repo_uses_repo_context_to_infer_crm_goal(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo-crm"
            repo.mkdir()
            (repo / "docs" / "crm-v2").mkdir(parents=True)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            (repo / "README.md").write_text("# Demo CRM\n")
            (repo / "CLAUDE.md").write_text("# CRM Workspace\n\nThis repo powers CRM V2 for leads, deals, and contact workflows.\n")
            (repo / "docs" / "crm-v2" / "overview.md").write_text(
                "# CRM V2\n\nThis app manages sales pipeline, contacts, and account records.\n"
            )
            (repo / "package.json").write_text(
                json.dumps(
                    {
                        "name": "crm-v2",
                        "description": "CRM platform for lead and deal management",
                        "scripts": {"test": "vitest"},
                    }
                )
            )
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.com",
                    "commit",
                    "-qm",
                    "init",
                ],
                cwd=repo,
                check=True,
            )

            env = os.environ.copy()
            env["COMPOUND_BRAIN_HOME"] = str(Path(tmp) / "claude-home")
            result = subprocess.run(
                ["python3", "scripts/activate_repo.py", "--project-dir", str(repo)],
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            state = json.loads((repo / ".brain" / "state" / "approval-state.json").read_text())
            inferred_goal = state["project_goal_candidates"][0].lower()
            self.assertIn("crm system", inferred_goal)
            self.assertIn("pipeline", inferred_goal)
            self.assertNotIn("trading system", inferred_goal)

    def test_activate_repo_confirm_persists_goal_and_departments(self) -> None:
        with TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            (repo / "README.md").write_text("# demo\n")
            subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.com",
                    "commit",
                    "-qm",
                    "init",
                ],
                cwd=repo,
                check=True,
            )

            env = os.environ.copy()
            env["COMPOUND_BRAIN_HOME"] = str(Path(tmp) / "claude-home")
            result = subprocess.run(
                [
                    "python3",
                    "scripts/activate_repo.py",
                    "--project-dir",
                    str(repo),
                    "--confirm",
                    "--project-goal",
                    "Ship CRM V2 reliably",
                    "--departments",
                    "engineering,product,operations",
                ],
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("next state: activated", result.stdout)
            state = json.loads((repo / ".brain" / "state" / "approval-state.json").read_text())
            self.assertEqual(state["state"], "approved")
            self.assertEqual(state["project_goal"], "Ship CRM V2 reliably")
            self.assertEqual(state["departments"], ["engineering", "product", "operations"])
