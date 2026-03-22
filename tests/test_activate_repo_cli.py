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
