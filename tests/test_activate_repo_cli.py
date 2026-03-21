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
