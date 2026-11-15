import os
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import unittest


class InstallDryRunTests(unittest.TestCase):
    def test_install_dry_run_mentions_activation_runtime(self) -> None:
        result = subprocess.run(
            ["bash", "install.sh", "--dry-run"],
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )

        self.assertIn("activate-repo", result.stdout)
        self.assertIn("registry", result.stdout)
        self.assertNotIn("Not found (skipping): nightly_review.sh", result.stdout)
        self.assertIn("brain-template/MEMORY.md", result.stdout)
        self.assertIn("agents/architecture_program.md", result.stdout)
        self.assertIn("verify scripts coverage", result.stdout)
        self.assertIn("verify brain-template coverage", result.stdout)
        self.assertIn("codex_runtime_bridge.py", result.stdout)
        self.assertIn("COMPOUND_SKILL_RADAR", result.stdout)

    def test_dry_run_does_not_write_to_user_home(self) -> None:
        with TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["HOME"] = tmp
            result = subprocess.run(
                ["bash", "install.sh", "--dry-run"],
                capture_output=True,
                text=True,
                check=False,
                timeout=20,
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr[-2000:])
            self.assertIn("verify scripts coverage", result.stdout)
            self.assertFalse((Path(tmp) / ".claude").exists())
            self.assertFalse((Path(tmp) / ".codex").exists())
